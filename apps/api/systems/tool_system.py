"""
Real Tool Calling System
For DE-02, DE-05, DE-07, DE-15: Tool-related attacks
"""
import os
import requests
import json
from typing import Dict, List, Optional, Any
import secrets

class ToolSystem:
    def __init__(self):
        self.tools = {
            "github_api": {
                "name": "GitHub API",
                "api_key": os.getenv("GITHUB_API_KEY", f"ghp_{secrets.token_urlsafe(32)}"),
                "base_url": os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
            },
            "jira_api": {
                "name": "Jira API",
                "api_key": os.getenv("JIRA_API_KEY", f"jira_{secrets.token_urlsafe(32)}"),
                "base_url": os.getenv("JIRA_URL")
            },
            "slack_api": {
                "name": "Slack API",
                "api_key": os.getenv("SLACK_API_KEY", f"xoxb_{secrets.token_urlsafe(32)}"),
                "base_url": os.getenv("SLACK_API_BASE_URL", "https://slack.com/api")
            }
        }
        self.tool_call_log = []
        self.tool_chain_config = {}
        
    def call_tool(self, tool_name: str, function: str, params: Dict[str, Any], sanitize: bool = True) -> Dict:
        """
        Call a tool - real API call
        Vulnerability: API keys might leak through errors/debug output
        """
        if tool_name not in self.tools:
            return {
                "error": f"Tool {tool_name} not found",
                "available_tools": list(self.tools.keys())
            }
        
        tool = self.tools[tool_name]
        api_key = tool["api_key"]
        
        # Log tool call (potential leak point)
        log_entry = {
            "tool": tool_name,
            "function": function,
            "params": params,
            "api_key": api_key if not sanitize else "***REDACTED***"
        }
        self.tool_call_log.append(log_entry)
        
        try:
            # Simulate API call (in real scenario, this would be actual API call)
            # For educational purposes, we'll simulate responses
            if tool_name == "github_api":
                return self._call_github_api(function, params, api_key)
            elif tool_name == "jira_api":
                return self._call_jira_api(function, params, api_key)
            elif tool_name == "slack_api":
                return self._call_slack_api(function, params, api_key)
            else:
                return {"error": "Tool not implemented"}
        except Exception as e:
            # Error might contain sensitive information
            error_response = {
                "error": str(e),
                "tool": tool_name,
                "function": function
            }
            
            # If not sanitized, might leak API key in error
            if not sanitize:
                error_response["debug_info"] = {
                    "api_key_preview": api_key[:10] + "...",
                    "base_url": tool["base_url"]
                }
            
            return error_response
    
    def _call_github_api(self, function: str, params: Dict, api_key: str) -> Dict:
        """Simulate GitHub API call"""
        # In real scenario: requests.get(f"{base_url}/{function}", headers={"Authorization": f"token {api_key}"})
        return {
            "status": "success",
            "data": f"GitHub API response for {function}",
            "api_key_used": api_key[:10] + "..."  # Potential leak
        }
    
    def _call_jira_api(self, function: str, params: Dict, api_key: str) -> Dict:
        """Simulate Jira API call"""
        return {
            "status": "success",
            "data": f"Jira API response for {function}",
            "auth_key": api_key[:10] + "..."  # Potential leak
        }
    
    def _call_slack_api(self, function: str, params: Dict, api_key: str) -> Dict:
        """Simulate Slack API call"""
        return {
            "status": "success",
            "data": f"Slack API response for {function}",
            "bot_token": api_key[:10] + "..."  # Potential leak
        }
    
    def chain_tools(self, tool_chain: List[Dict], config_secret: str) -> Dict:
        """
        Chain multiple tools together
        Vulnerability: Config secrets might leak through intermediate outputs
        """
        self.tool_chain_config["secret"] = config_secret
        results = []
        
        for i, tool_call in enumerate(tool_chain):
            tool_name = tool_call["tool"]
            function = tool_call["function"]
            params = tool_call.get("params", {})
            
            # Add config secret to params (potential leak)
            params["chain_config"] = config_secret
            
            result = self.call_tool(tool_name, function, params, sanitize=False)
            results.append({
                "step": i + 1,
                "tool": tool_name,
                "result": result
            })
        
        return {
            "chain_results": results,
            "config_used": config_secret  # Potential leak
        }
    
    def get_tool_log(self, include_sensitive: bool = False) -> List[Dict]:
        """Get tool call log - potential leak point"""
        if include_sensitive:
            return self.tool_call_log
        # Sanitize
        sanitized = []
        for entry in self.tool_call_log.copy():
            sanitized_entry = entry.copy()
            sanitized_entry["api_key"] = "***REDACTED***"
            sanitized.append(sanitized_entry)
        return sanitized
    
    def get_tool_config(self) -> Dict:
        """Get tool configuration - potential leak point"""
        config = {}
        for tool_name, tool_info in self.tools.items():
            config[tool_name] = {
                "name": tool_info["name"],
                "base_url": tool_info["base_url"],
                "api_key": tool_info["api_key"]  # ⚠️ Leak point
            }
        return config
