#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android UI Hierarchy Information Extractor
Execute adb commands to get UI dump and parse useful node information
"""

from .common import app

import subprocess
import xml.etree.ElementTree as ET
import json
from typing import List, Dict, Optional


class UINode:
    """UI Node Information Class"""
    def __init__(self, text: str = "", resource_id: str = "", content_desc: str = "", bounds: str = ""):
        self.text = text
        self.resource_id = resource_id
        self.content_desc = content_desc
        self.bounds = bounds
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format"""
        return {
            'text': self.text,
            'resource_id': self.resource_id,
            'content_desc': self.content_desc,
            'bounds': self.bounds
        }
    
    def __str__(self) -> str:
        return f"UINode(text='{self.text}', resource_id='{self.resource_id}', content_desc='{self.content_desc}', bounds='{self.bounds}')"


class UIHierarchyExtractor:
    """UI Hierarchy Information Extractor"""
    
    def __init__(self):
        self.xml_content = ""
        self.nodes = []
    
    def execute_adb_commands(self) -> bool:
        """Execute adb commands to get UI dump"""
        try:
            # Execute uiautomator dump command
            print("Executing uiautomator dump...")
            dump_result = subprocess.run(
                ["adb", "shell", "uiautomator", "dump"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            
            if dump_result.returncode != 0:
                print(f"uiautomator dump execution failed: {dump_result.stderr}")
                return False
            
            print("uiautomator dump executed successfully")
            
            # Get XML content
            print("Getting XML file content...")
            cat_result = subprocess.run(
                ["adb", "shell", "cat", "/sdcard/window_dump.xml"],
                capture_output=True,
                text=False,  # Get byte data first
                timeout=30
            )
            
            if cat_result.returncode != 0:
                print(f"Failed to get XML file: {cat_result.stderr.decode('utf-8', errors='ignore')}")
                return False
            
            # Try multiple encoding methods to decode XML content
            xml_bytes = cat_result.stdout
            encodings_to_try = ['utf-8', 'utf-8-sig', 'gb2312', 'gbk', 'latin1']
            
            for encoding in encodings_to_try:
                try:
                    self.xml_content = xml_bytes.decode(encoding)
                    print(f"XML file obtained successfully (using {encoding} encoding)")
                    return True
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use error ignoring mode
            try:
                self.xml_content = xml_bytes.decode('utf-8', errors='ignore')
                print("XML file obtained successfully (using UTF-8 encoding, ignoring error characters)")
                return True
            except Exception:
                print("Unable to decode XML content")
                return False
            
        except subprocess.TimeoutExpired:
            print("Command execution timed out")
            return False
        except FileNotFoundError:
            print("adb command not found, please ensure adb is installed and in PATH")
            return False
        except Exception as e:
            print(f"Error occurred while executing command: {e}")
            return False
    
    def parse_xml_content(self) -> bool:
        """Parse XML content"""
        if not self.xml_content:
            print("XML content is empty")
            return False
        
        try:
            # Parse XML
            root = ET.fromstring(self.xml_content)
            self._extract_nodes(root)
            print(f"XML parsed successfully, found {len(self.nodes)} valid nodes")
            return True
            
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return False
        except Exception as e:
            print(f"Error occurred while parsing XML: {e}")
            return False
    
    def _extract_nodes(self, element: ET.Element):
        """Recursively extract node information"""
        # Get node attributes
        text = element.get('text', '').strip()
        resource_id = element.get('resource-id', '').strip()
        content_desc = element.get('content-desc', '').strip()
        bounds = element.get('bounds', '').strip()
        
        # Check if any of the fields have values
        if text or resource_id or content_desc:
            node = UINode(text, resource_id, content_desc, bounds)
            self.nodes.append(node)
        
        # Recursively process child nodes
        for child in element:
            self._extract_nodes(child)
    
    def get_nodes_info(self) -> List[Dict[str, str]]:
        """Get list of node information"""
        return [node.to_dict() for node in self.nodes]
    
    def print_nodes_summary(self):
        """Print node summary information"""
        print(f"\n=== Found {len(self.nodes)} valid nodes ===")
        
        text_count = sum(1 for node in self.nodes if node.text)
        resource_id_count = sum(1 for node in self.nodes if node.resource_id)
        content_desc_count = sum(1 for node in self.nodes if node.content_desc)
        
        print(f"Nodes with text: {text_count}")
        print(f"Nodes with resource-id: {resource_id_count}")
        print(f"Nodes with content-desc: {content_desc_count}")
    
    def print_nodes_detail(self, max_display: int = 10):
        """Print detailed node information"""
        print(f"\n=== Node Detailed Information (displaying first {min(max_display, len(self.nodes))} nodes) ===")
        
        for i, node in enumerate(self.nodes[:max_display]):
            print(f"\nNode {i+1}:")
            print(f"  text: '{node.text}'")
            print(f"  resource-id: '{node.resource_id}'")
            print(f"  content-desc: '{node.content_desc}'")
            print(f"  bounds: '{node.bounds}'")
        
        if len(self.nodes) > max_display:
            print(f"\n... and {len(self.nodes) - max_display} more nodes")
    
    def save_to_json(self, filename: str = "ui_nodes.json"):
        """Save results to JSON file"""
        try:
            data = {
                'total_nodes': len(self.nodes),
                'nodes': self.get_nodes_info()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Results saved to file: {filename}")
            
        except Exception as e:
            print(f"Error occurred while saving file: {e}")
    
    def save_xml(self, filename: str = "ui_dump.xml"):
        """Save original XML file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.xml_content)
            print(f"Original XML saved to file: {filename}")
        except Exception as e:
            print(f"Error occurred while saving XML file: {e}")


@app.tool()
def tool_get_ui_dump():
    """
    Tool function to get UI hierarchy structure information of current Android device interface
    
    This function obtains the current interface UI information of the connected device through ADB commands,
    including text, resource ID, content description, and boundary coordinates, and parses this information
    into structured data.
    
    Returns:
        List[Dict[str, str]]: Dictionary list containing UI node information, each dictionary includes:
            - text: Node text content
            - resource_id: Resource ID
            - content_desc: Content description
            - bounds: Boundary coordinate information
        str: Returns error message on execution failure
    """
    # Create UI hierarchy information extractor instance
    extractor = UIHierarchyExtractor()
    
    # Execute ADB commands to get UI dump information, return error message on failure
    if not extractor.execute_adb_commands():
        return "Failed to get UI dump, program exit"
    
    # Parse the obtained XML content, return error message on failure
    if not extractor.parse_xml_content():
        return "Failed to parse XML, program exit"
    
    # Return the parsed node information list
    return extractor.get_nodes_info()