"""TCGA-BRCA longitudinal sample matching (metadata-level, Plan 02 / #355).

Visit ordering uses ``days_to_collection`` when present, then ``sample_type_rank``
from ``src/config/longitudinal_keys.yaml``. Case-level clinical timestamps are
documented in ``src/data/clinical_time.py`` (not used for per-sample ordering here).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from src.config.load_config import brca_gdc_keys


@dataclass
class SampleVisit:
    case_id: str
    submitter_id: str
    sample_id: str
    sample_submitter_id: str
    sample_type: str
    days_to_collection: float | None
    visit_index: int | None = None
    order_source: str = "unknown"


@dataclass
class MatchPair:
    case_id: str
    submitter_id: str
    anchor_sample_id: str
    anchor_sample_type: str
    later_sample_id: str
    later_sample_type: str
    anchor_visit_index: int
    later_visit_index: int


@dataclass
class CaseMatchingResult:
    case_id: str
    submitter_id: str
    visits: list[SampleVisit] = field(default_factory=list)
    pairs: list[MatchPair] = field(default_factory=list)
    excluded: bool = False
    exclusion_reason: str | None = None
    n_samples_dropped_unranked: int = 0


def _parse_days(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_gdc_case(case: Mapping[str, Any], gdc_keys: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten one GDC cases API hit into patient + sample records."""
    patient = gdc_keys.get("patient") or {}
    sample_cfg = gdc_keys.get("sample") or {}
    case_id = case.get(patient.get("case_id_field", "case_id"))
    submitter_id = case.get(patient.get("submitter_id_field", "submitter_id")) or case_id
    samples_raw = case.get("samples") or []
    samples: list[dict[str, Any]] = []
    st_field = sample_cfg.get("sample_type_field", "sample_type")
    time_primary = (sample_cfg.get("time_fields") or {}).get("primary", "days_to_collection")
    sid_field = sample_cfg.get("sample_id_field", "sample_id")
    ssub_field = sample_cfg.get("submitter_id_field", "submitter_id")
    for row in samples_raw:
        if not isinstance(row, dict):
            continue
        sample_type = row.get(st_field)
        if not sample_type:
            continue
        samples.append(
            {
                "sample_id": row.get(sid_field),
                "sample_submitter_id": row.get(ssub_field) or row.get(sid_field),
                "sample_type": str(sample_type),
                "days_to_collection": _parse_days(row.get(time_primary)),
            }
        )
    return {
        "case_id": case_id,
        "submitter_id": submitter_id,
        "samples": samples,
    }


def _rank(sample_type: str, rank_map: Mapping[str, int]) -> int | None:
    if sample_type in rank_map:
        return int(rank_map[sample_type])
    return None


def _drop_unranked_enabled(gdc_keys: Mapping[str, Any]) -> bool:
    exclusions = gdc_keys.get("exclusions") or {}
    if "drop_unranked_sample_types" in exclusions:
        return bool(exclusions["drop_unranked_sample_types"])
    sample_filter = gdc_keys.get("sample_filter") or {}
    return bool(sample_filter.get("drop_unranked_sample_types", True))


def filter_ranked_samples(
    samples: Sequence[Mapping[str, Any]],
    gdc_keys: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], int]:
    """Keep samples whose ``sample_type`` is in ``sample_type_rank`` when drop is enabled."""
    rank_map = gdc_keys.get("sample_type_rank") or {}
    if not _drop_unranked_enabled(gdc_keys):
        return list(samples), 0
    ranked: list[Mapping[str, Any]] = []
    n_dropped = 0
    for s in samples:
        st = str(s.get("sample_type", ""))
        if st in rank_map:
            ranked.append(s)
        else:
            n_dropped += 1
    return ranked, n_dropped


def order_visits(
    samples: Sequence[Mapping[str, Any]],
    gdc_keys: Mapping[str, Any],
) -> tuple[list[SampleVisit], str | None]:
    """Order samples within a case; return (visits, exclusion_reason)."""
    rank_map = gdc_keys.get("sample_type_rank") or {}
    if len(samples) < 2:
        return [], "single_sample_case"

    typed: list[tuple[Mapping[str, Any], int | None]] = []
    for s in samples:
        st = str(s.get("sample_type", ""))
        typed.append((s, _rank(st, rank_map)))

    if any(r is None for _, r in typed):
        return [], "missing_time_and_rank"

    # Ambiguous duplicate sample_type when time is missing for any involved sample.
    type_counts = Counter(str(s.get("sample_type")) for s in samples)
    dup_types = {t for t, c in type_counts.items() if c > 1}
    if dup_types:
        for s in samples:
            if str(s.get("sample_type")) in dup_types and s.get("days_to_collection") is None:
                return [], "ambiguous_duplicate_sample_type_without_time"

    def sort_key(item: tuple[Mapping[str, Any], int | None]) -> tuple[float, int, str]:
        s, rank = item
        days = s.get("days_to_collection")
        if days is not None:
            return (float(days), int(rank or 0), str(s.get("sample_submitter_id", "")))
        return (float("inf"), int(rank or 0), str(s.get("sample_submitter_id", "")))

    ordered = sorted(typed, key=sort_key)
    visits: list[SampleVisit] = []
    for idx, (s, _) in enumerate(ordered):
        days = s.get("days_to_collection")
        order_source = "days_to_collection" if days is not None else "sample_type_rank"
        visits.append(
            SampleVisit(
                case_id=str(s.get("case_id", "")),
                submitter_id=str(s.get("submitter_id", "")),
                sample_id=str(s.get("sample_id", "")),
                sample_submitter_id=str(s.get("sample_submitter_id", "")),
                sample_type=str(s.get("sample_type", "")),
                days_to_collection=_parse_days(days),
                visit_index=idx,
                order_source=order_source,
            )
        )
    return visits, None


def build_match_pairs(
    visits: Sequence[SampleVisit],
    gdc_keys: Mapping[str, Any],
) -> list[MatchPair]:
    """Directed anchor→later pairs per YAML match_pair rules."""
    cfg = gdc_keys.get("match_pair") or {}
    anchors = set(cfg.get("anchor_sample_types") or [])
    later = set(cfg.get("later_sample_types") or [])
    pairs: list[MatchPair] = []
    if len(visits) < 2:
        return pairs
    for i, anchor in enumerate(visits):
        if anchor.sample_type not in anchors:
            continue
        for j in range(i + 1, len(visits)):
            nxt = visits[j]
            if nxt.sample_type not in later:
                continue
            pairs.append(
                MatchPair(
                    case_id=anchor.case_id,
                    submitter_id=anchor.submitter_id,
                    anchor_sample_id=anchor.sample_id,
                    anchor_sample_type=anchor.sample_type,
                    later_sample_id=nxt.sample_id,
                    later_sample_type=nxt.sample_type,
                    anchor_visit_index=int(anchor.visit_index or i),
                    later_visit_index=int(nxt.visit_index or j),
                )
            )
    return pairs


def process_case(
    case: Mapping[str, Any],
    gdc_keys: Mapping[str, Any],
) -> CaseMatchingResult:
    """Run ordering, exclusions, and pair generation for one normalized case."""
    case_id = str(case.get("case_id", ""))
    submitter_id = str(case.get("submitter_id") or case_id)
    raw_samples = case.get("samples") or []
    enriched = [
        {
            **dict(s),
            "case_id": case_id,
            "submitter_id": submitter_id,
        }
        for s in raw_samples
    ]
    ranked_samples, n_dropped = filter_ranked_samples(enriched, gdc_keys)
    if not ranked_samples:
        return CaseMatchingResult(
            case_id=case_id,
            submitter_id=submitter_id,
            excluded=True,
            exclusion_reason="no_ranked_samples",
            n_samples_dropped_unranked=n_dropped,
        )
    visits, reason = order_visits(ranked_samples, gdc_keys)
    if reason:
        return CaseMatchingResult(
            case_id=case_id,
            submitter_id=submitter_id,
            excluded=True,
            exclusion_reason=reason,
            n_samples_dropped_unranked=n_dropped,
        )
    for v in visits:
        v.case_id = case_id
        v.submitter_id = submitter_id
    pairs = build_match_pairs(visits, gdc_keys)
    return CaseMatchingResult(
        case_id=case_id,
        submitter_id=submitter_id,
        visits=visits,
        pairs=pairs,
        n_samples_dropped_unranked=n_dropped,
    )


def process_cohort(
    cases: Sequence[Mapping[str, Any]],
    gdc_keys: Mapping[str, Any] | None = None,
) -> list[CaseMatchingResult]:
    gdc_keys = gdc_keys or brca_gdc_keys()
    normalized = [normalize_gdc_case(c, gdc_keys) for c in cases]
    return [process_case(c, gdc_keys) for c in normalized]


def summarize_cohort(
    results: Sequence[CaseMatchingResult],
    *,
    schema_version: int = 1,
    project_id: str = "TCGA-BRCA",
    n_cases_queried: int | None = None,
) -> dict[str, Any]:
    """Build summary.json payload."""
    exclusion_counts: Counter[str] = Counter()
    n_visit_sequences = 0
    n_match_pairs = 0
    n_multi = 0
    n_samples_dropped_unranked = 0
    for r in results:
        n_samples_dropped_unranked += r.n_samples_dropped_unranked
        if r.excluded:
            if r.exclusion_reason:
                exclusion_counts[r.exclusion_reason] += 1
            continue
        if len(r.visits) >= 2:
            n_multi += 1
            n_visit_sequences += 1
            n_match_pairs += len(r.pairs)
    return {
        "schema_version": schema_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_id": project_id,
        "n_cases_queried": n_cases_queried if n_cases_queried is not None else len(results),
        "n_cases": len(results),
        "n_multi_sample_cases": n_multi,
        "n_visit_sequences": n_visit_sequences,
        "n_match_pairs": n_match_pairs,
        "n_samples_dropped_unranked": n_samples_dropped_unranked,
        "exclusion_counts": dict(sorted(exclusion_counts.items())),
    }


def visit_sequences_document(results: Sequence[CaseMatchingResult]) -> dict[str, Any]:
    sequences = []
    for r in results:
        if r.excluded or len(r.visits) < 2:
            continue
        sequences.append(
            {
                "case_id": r.case_id,
                "submitter_id": r.submitter_id,
                "n_visits": len(r.visits),
                "visits": [
                    {
                        "visit_index": v.visit_index,
                        "sample_id": v.sample_id,
                        "sample_submitter_id": v.sample_submitter_id,
                        "sample_type": v.sample_type,
                        "days_to_collection": v.days_to_collection,
                        "order_source": v.order_source,
                    }
                    for v in r.visits
                ],
            }
        )
    return {"schema_version": 1, "visit_sequences": sequences}


def match_pairs_document(results: Sequence[CaseMatchingResult]) -> dict[str, Any]:
    pairs = []
    for r in results:
        for p in r.pairs:
            pairs.append(
                {
                    "case_id": p.case_id,
                    "submitter_id": p.submitter_id,
                    "anchor_sample_id": p.anchor_sample_id,
                    "anchor_sample_type": p.anchor_sample_type,
                    "later_sample_id": p.later_sample_id,
                    "later_sample_type": p.later_sample_type,
                    "anchor_visit_index": p.anchor_visit_index,
                    "later_visit_index": p.later_visit_index,
                }
            )
    return {"schema_version": 1, "match_pairs": pairs}
