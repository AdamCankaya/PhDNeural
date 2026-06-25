"""GitHub GraphQL client for Projects v2 and issue management."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


class GitHubApiError(RuntimeError):
    """Raised when the GitHub API returns an error."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.errors = errors or []


@dataclass
class ProjectFieldInfo:
    field_id: str
    field_name: str
    field_type: str
    options: dict[str, str]  # option name -> option id


@dataclass
class RepositoryInfo:
    node_id: str
    owner: str
    name: str


@dataclass
class ProjectInfo:
    project_id: str
    title: str
    url: str
    fields: dict[str, ProjectFieldInfo]


class GitHubProjectsClient:
    """Minimal GraphQL client for syncing issues into GitHub Projects v2."""

    def __init__(self, token: str, dry_run: bool = False):
        self.token = token
        self.dry_run = dry_run

    def _request(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.dry_run and query.strip().startswith("mutation"):
            return {"data": {}}

        payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
        req = urllib.request.Request(
            GITHUB_GRAPHQL_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "phd-github-sync",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubApiError(f"HTTP {exc.code}: {detail}") from exc

        if body.get("errors"):
            raise GitHubApiError("GraphQL error", errors=body["errors"])
        return body

    def get_repository(self, owner: str, repo: str) -> RepositoryInfo:
        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            id
          }
        }
        """
        data = self._request(query, {"owner": owner, "repo": repo})["data"]
        node_id = data["repository"]["id"]
        return RepositoryInfo(node_id=node_id, owner=owner, name=repo)

    def get_project(
        self, owner: str, project_number: int, repo: str | None = None
    ) -> ProjectInfo:
        project_fragment = """
              id
              title
              url
              fields(first: 50) {
                nodes {
                  ... on ProjectV2FieldCommon {
                    id
                    name
                    dataType
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    dataType
                    options {
                      id
                      name
                    }
                  }
                }
              }
        """

        project = None
        if repo:
            query = f"""
            query($owner: String!, $repo: String!, $number: Int!) {{
              repository(owner: $owner, name: $repo) {{
                projectV2(number: $number) {{{project_fragment}
                }}
              }}
            }}
            """
            body = self._request(
                query, {"owner": owner, "repo": repo, "number": project_number}
            )
            if not body.get("errors"):
                repo_node = body.get("data", {}).get("repository")
                if repo_node:
                    project = repo_node.get("projectV2")

        if not project:
            for owner_kind in ("user", "organization"):
                query = f"""
                query($owner: String!, $number: Int!) {{
                  {owner_kind}(login: $owner) {{
                    projectV2(number: $number) {{{project_fragment}
                    }}
                  }}
                }}
                """
                body = self._request(query, {"owner": owner, "number": project_number})
                if body.get("errors"):
                    continue
                data = body["data"]
                owner_node = data.get(owner_kind)
                if owner_node:
                    project = owner_node.get("projectV2")
                if project:
                    break

        if not project:
            scope_hint = f"repository {owner}/{repo}" if repo else f"owner '{owner}'"
            raise GitHubApiError(
                f"Project #{project_number} not found for {scope_hint}. "
                "Check GITHUB_OWNER, GITHUB_REPO, and GITHUB_PROJECT_NUMBER."
            )

        fields: dict[str, ProjectFieldInfo] = {}
        for node in project["fields"]["nodes"]:
            if not node:
                continue
            options = {}
            if "options" in node and node["options"]:
                options = {opt["name"]: opt["id"] for opt in node["options"]}
            fields[node["name"].lower()] = ProjectFieldInfo(
                field_id=node["id"],
                field_name=node["name"],
                field_type=node["dataType"],
                options=options,
            )

        return ProjectInfo(
            project_id=project["id"],
            title=project["title"],
            url=project["url"],
            fields=fields,
        )

    def ensure_label(self, repo_node_id: str, label_name: str, color: str = "1d76db") -> str:
        query = """
        query($repoId: ID!, $cursor: String) {
          node(id: $repoId) {
            ... on Repository {
              labels(first: 100, after: $cursor) {
                nodes { id name }
                pageInfo { hasNextPage endCursor }
              }
            }
          }
        }
        """
        cursor = None
        while True:
            data = self._request(query, {"repoId": repo_node_id, "cursor": cursor})["data"]
            labels = data["node"]["labels"]
            for label in labels["nodes"]:
                if label["name"] == label_name:
                    return label["id"]
            if not labels["pageInfo"]["hasNextPage"]:
                break
            cursor = labels["pageInfo"]["endCursor"]

        if self.dry_run:
            return f"dry-run-label-{label_name}"

        mutation = """
        mutation($repoId: ID!, $name: String!, $color: String!) {
          createLabel(input: {repositoryId: $repoId, name: $name, color: $color}) {
            label { id }
          }
        }
        """
        result = self._request(
            mutation, {"repoId": repo_node_id, "name": label_name, "color": color}
        )
        return result["data"]["createLabel"]["label"]["id"]

    def list_synced_issues(self, owner: str, repo: str) -> dict[str, dict[str, Any]]:
        """Return existing phd-sync issues keyed by sync-id parsed from body."""
        all_issues = self.list_all_synced_issues(owner, repo)
        found: dict[str, dict[str, Any]] = {}
        for issue in all_issues:
            sync_id = issue.get("sync_id")
            if sync_id:
                found[sync_id] = issue
        return found

    def list_all_synced_issues(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Return every phd-sync issue, including duplicate sync-id entries."""
        query = """
        query($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            issues(
              first: 50
              after: $cursor
              labels: ["phd-sync"]
              states: [OPEN, CLOSED]
              orderBy: {field: CREATED_AT, direction: ASC}
            ) {
              nodes {
                number
                id
                title
                state
                body
              }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
        """
        sync_id_re = __import__("re").compile(r"phd-sync-id:\s*([^\s>]+)")
        found: list[dict[str, Any]] = []
        cursor = None
        while True:
            data = self._request(query, {"owner": owner, "repo": repo, "cursor": cursor})["data"]
            issues = data["repository"]["issues"]
            for issue in issues["nodes"]:
                body = issue.get("body") or ""
                match = sync_id_re.search(body)
                issue["sync_id"] = match.group(1) if match else None
                found.append(issue)
            if not issues["pageInfo"]["hasNextPage"]:
                break
            cursor = issues["pageInfo"]["endCursor"]
        return found

    def create_issue(
        self,
        repo_node_id: str,
        title: str,
        body: str,
        label_ids: list[str],
    ) -> dict[str, Any]:
        if self.dry_run:
            return {"id": f"dry-run-issue-{slug_safe(title)}", "number": 0}

        mutation = """
        mutation($repoId: ID!, $title: String!, $body: String!, $labelIds: [ID!]) {
          createIssue(
            input: {repositoryId: $repoId, title: $title, body: $body, labelIds: $labelIds}
          ) {
            issue { id number url }
          }
        }
        """
        result = self._request(
            mutation,
            {
                "repoId": repo_node_id,
                "title": title,
                "body": body,
                "labelIds": label_ids,
            },
        )
        return result["data"]["createIssue"]["issue"]

    def update_issue(self, issue_id: str, title: str, body: str) -> None:
        if self.dry_run:
            return
        mutation = """
        mutation($id: ID!, $title: String!, $body: String!) {
          updateIssue(input: {id: $id, title: $title, body: $body}) {
            issue { id }
          }
        }
        """
        self._request(mutation, {"id": issue_id, "title": title, "body": body})

    def close_issue(self, issue_id: str, reason: str = "") -> None:
        if self.dry_run:
            return
        mutation = """
        mutation($id: ID!, $state: IssueState!) {
          updateIssue(input: {id: $id, state: $state}) {
            issue { id state }
          }
        }
        """
        self._request(mutation, {"id": issue_id, "state": "CLOSED"})
        if reason:
            comment_mutation = """
            mutation($subjectId: ID!, $body: String!) {
              addComment(input: {subjectId: $subjectId, body: $body}) {
                commentEdge { node { id } }
              }
            }
            """
            body = f"Closed automatically: {reason}"
            self._request(comment_mutation, {"subjectId": issue_id, "body": body})

    def add_issue_to_project(self, project_id: str, issue_node_id: str) -> str:
        if self.dry_run:
            return f"dry-run-item-{issue_node_id[-8:]}"

        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        result = self._request(
            mutation, {"projectId": project_id, "contentId": issue_node_id}
        )
        return result["data"]["addProjectV2ItemById"]["item"]["id"]

    def list_project_items(self, project_id: str) -> list[dict[str, Any]]:
        """Return all project items with issue metadata and Status field value."""
        query = """
        query($projectId: ID!, $cursor: String) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100, after: $cursor) {
                nodes {
                  id
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field { ... on ProjectV2SingleSelectField { name } }
                      }
                    }
                  }
                  content {
                    ... on Issue {
                      id
                      number
                      title
                      state
                      body
                    }
                  }
                }
                pageInfo { hasNextPage endCursor }
              }
            }
          }
        }
        """
        import re

        sync_id_re = re.compile(r"phd-sync-id:\s*([^\s>]+)")
        results: list[dict[str, Any]] = []
        cursor = None
        while True:
            data = self._request(query, {"projectId": project_id, "cursor": cursor})["data"]
            items = data["node"]["items"]
            for item in items["nodes"]:
                content = item.get("content") or {}
                body = content.get("body") or ""
                match = sync_id_re.search(body)
                status = None
                for fv in item.get("fieldValues", {}).get("nodes", []):
                    field = (fv.get("field") or {}).get("name", "")
                    if field.lower() == "status":
                        status = fv.get("name")
                        break
                results.append(
                    {
                        "project_item_id": item["id"],
                        "issue_node_id": content.get("id"),
                        "issue_number": content.get("number"),
                        "issue_title": content.get("title"),
                        "issue_state": content.get("state"),
                        "sync_id": match.group(1) if match else None,
                        "status": status,
                    }
                )
            if not items["pageInfo"]["hasNextPage"]:
                break
            cursor = items["pageInfo"]["endCursor"]
        return results

    def delete_project_item(self, project_id: str, item_id: str) -> None:
        if self.dry_run:
            return
        mutation = """
        mutation($projectId: ID!, $itemId: ID!) {
          deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) {
            deletedItemId
          }
        }
        """
        self._request(mutation, {"projectId": project_id, "itemId": item_id})

    def get_project_item_for_issue(self, project_id: str, issue_node_id: str) -> str | None:
        for item in self.list_project_items(project_id):
            if item.get("issue_node_id") == issue_node_id:
                return item["project_item_id"]
        return None

    def get_all_project_items_for_issue(
        self, project_id: str, issue_node_id: str
    ) -> list[str]:
        return [
            item["project_item_id"]
            for item in self.list_project_items(project_id)
            if item.get("issue_node_id") == issue_node_id
        ]

    def set_text_field(
        self, project_id: str, item_id: str, field_id: str, value: str
    ) -> None:
        if self.dry_run:
            return
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: { text: $value }
            }
          ) {
            projectV2Item { id }
          }
        }
        """
        self._request(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "value": value,
            },
        )

    def set_single_select_field(
        self, project_id: str, item_id: str, field_id: str, option_id: str
    ) -> None:
        if self.dry_run:
            return
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: { singleSelectOptionId: $optionId }
            }
          ) {
            projectV2Item { id }
          }
        }
        """
        self._request(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "optionId": option_id,
            },
        )

    def ensure_single_select_field(
        self,
        project_id: str,
        field_name: str,
        option_names: list[str],
        existing_fields: dict[str, ProjectFieldInfo],
    ) -> ProjectFieldInfo:
        key = field_name.lower()
        if key in existing_fields:
            field = existing_fields[key]
            missing = [name for name in option_names if name not in field.options]
            if not missing or self.dry_run:
                return field
            mutation = """
            mutation($fieldId: ID!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
              updateProjectV2Field(
                input: {fieldId: $fieldId, singleSelectOptions: $options}
              ) {
                projectV2Field {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options { id name }
                  }
                }
              }
            }
            """
            options_input = [{"name": name, "description": name, "color": "GRAY"} for name in field.options.keys()] + [
                {"name": name, "description": name, "color": "GRAY"} for name in missing
            ]
            result = self._request(
                mutation, {"fieldId": field.field_id, "options": options_input}
            )
            node = result["data"]["updateProjectV2Field"]["projectV2Field"]
            options = {opt["name"]: opt["id"] for opt in node["options"]}
            updated = ProjectFieldInfo(
                field_id=node["id"],
                field_name=node["name"],
                field_type="SINGLE_SELECT",
                options=options,
            )
            existing_fields[key] = updated
            return updated

        if self.dry_run:
            info = ProjectFieldInfo(
                field_id=f"dry-run-field-{slug_safe(field_name)}",
                field_name=field_name,
                field_type="SINGLE_SELECT",
                options={name: f"dry-opt-{slug_safe(name)}" for name in option_names},
            )
            existing_fields[key] = info
            return info

        mutation = """
        mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
          createProjectV2Field(
            input: {
              projectId: $projectId
              dataType: SINGLE_SELECT
              name: $name
              singleSelectOptions: $options
            }
          ) {
            projectV2Field {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
            }
          }
        }
        """
        options_input = [{"name": name, "description": name, "color": "GRAY"} for name in option_names]
        result = self._request(
            mutation,
            {"projectId": project_id, "name": field_name, "options": options_input},
        )
        node = result["data"]["createProjectV2Field"]["projectV2Field"]
        options = {opt["name"]: opt["id"] for opt in node["options"]}
        info = ProjectFieldInfo(
            field_id=node["id"],
            field_name=node["name"],
            field_type="SINGLE_SELECT",
            options=options,
        )
        existing_fields[key] = info
        return info

    def ensure_text_field(
        self,
        project_id: str,
        field_name: str,
        existing_fields: dict[str, ProjectFieldInfo],
    ) -> ProjectFieldInfo:
        key = field_name.lower()
        if key in existing_fields:
            return existing_fields[key]

        if self.dry_run:
            info = ProjectFieldInfo(
                field_id=f"dry-run-field-{slug_safe(field_name)}",
                field_name=field_name,
                field_type="TEXT",
                options={},
            )
            existing_fields[key] = info
            return info

        mutation = """
        mutation($projectId: ID!, $name: String!) {
          createProjectV2Field(
            input: {projectId: $projectId, dataType: TEXT, name: $name}
          ) {
            projectV2Field {
              ... on ProjectV2FieldCommon {
                id
                name
                dataType
              }
            }
          }
        }
        """
        result = self._request(
            mutation, {"projectId": project_id, "name": field_name}
        )
        node = result["data"]["createProjectV2Field"]["projectV2Field"]
        info = ProjectFieldInfo(
            field_id=node["id"],
            field_name=node["name"],
            field_type=node["dataType"],
            options={},
        )
        existing_fields[key] = info
        return info


def slug_safe(text: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in text.lower())[:40]


def load_config() -> dict[str, str]:
    """Load configuration from environment variables and optional config file."""
    config: dict[str, str] = {}

    config_path = os.environ.get(
        "PHD_SYNC_CONFIG",
        str(Path_default_config()),
    )
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as fh:
            file_config = json.load(fh)
        config.update({k: str(v) for k, v in file_config.items() if v is not None})

    for key in (
        "GITHUB_TOKEN",
        "GITHUB_OWNER",
        "GITHUB_REPO",
        "GITHUB_PROJECT_NUMBER",
        "PHD_PLAN_PATH",
        "PHD_SYNC_STATE_PATH",
    ):
        if os.environ.get(key):
            config[key] = os.environ[key]

    token = config.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
    if token:
        config["GITHUB_TOKEN"] = token

    return config


def Path_default_config() -> str:
    from pathlib import Path

    return str(Path(__file__).resolve().parent.parent / "bio-nas_github_sync.config.json")


def resolve_token(config: dict[str, str]) -> str:
    token = config.get("GITHUB_TOKEN", "")
    if token:
        return token
    # Fall back to gh CLI credential helper output.
    import subprocess

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def validate_config(config: dict[str, str]) -> None:
    missing = []
    if not resolve_token(config):
        missing.append("GITHUB_TOKEN (or run `gh auth login`)")
    for key in ("GITHUB_OWNER", "GITHUB_REPO", "GITHUB_PROJECT_NUMBER"):
        if not config.get(key):
            missing.append(key)
    if missing:
        raise ValueError(
            "Missing required configuration:\n  - " + "\n  - ".join(missing)
        )
