
#!/usr/bin/env python3
"""
Aegis OS Code Obfuscation System
Protects source code from reverse engineering
"""

import os
import re
import base64
import random
import string
import ast
import sys
from pathlib import Path

class AegisObfuscator:
    def __init__(self):
        self.var_map = {}
        self.func_map = {}
        self.string_map = {}
        
    def generate_random_name(self, length=8):
        """Generate random variable/function name"""
        chars = string.ascii_letters + '_'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def obfuscate_strings(self, code):
        """Encode strings to base64"""
        def replace_string(match):
            original = match.group(0)
            content = match.group(1)
            if len(content) < 5:  # Skip very short strings
                return original
            
            # Encode to base64
            encoded = base64.b64encode(content.encode()).decode()
            key = f"_s{len(self.string_map)}"
            self.string_map[key] = encoded
            
            return f'base64.b64decode({key}).decode()'
        
        # Replace string literals
        code = re.sub(r'"([^"]{5,})"', replace_string, code)
        code = re.sub(r"'([^']{5,})'", replace_string, code)
        
        return code
    
    def obfuscate_variables(self, code):
        """Rename variables to random names"""
        # Find variable assignments
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        
        for match in re.finditer(var_pattern, code):
            var_name = match.group(1)
            if var_name not in ['self', 'cls'] and not var_name.startswith('__'):
                if var_name not in self.var_map:
                    self.var_map[var_name] = self.generate_random_name()
        
        # Replace variables
        for original, obfuscated in self.var_map.items():
            code = re.sub(rf'\b{original}\b', obfuscated, code)
        
        return code
    
    def obfuscate_functions(self, code):
        """Rename function definitions"""
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            if not func_name.startswith('__') and func_name != 'main':
                if func_name not in self.func_map:
                    self.func_map[func_name] = self.generate_random_name()
        
        # Replace function definitions and calls
        for original, obfuscated in self.func_map.items():
            code = re.sub(rf'\bdef\s+{original}\b', f'def {obfuscated}', code)
            code = re.sub(rf'\b{original}\s*\(', f'{obfuscated}(', code)
        
        return code
    
    def add_dummy_code(self, code):
        """Add dummy code to confuse reverse engineering"""
        dummy_functions = [
            "def _dummy_auth(): return True",
            "def _dummy_check(): pass",
            "_dummy_var = 'AEGIS_DECOY'",
            "_dummy_list = [1, 2, 3, 4, 5]"
        ]
        
        return '\n'.join(dummy_functions) + '\n\n' + code
    
    def create_header(self):
        """Create obfuscated header"""
        header = []
        header.append("import base64")
        
        # Add string map
        for key, encoded in self.string_map.items():
            header.append(f"{key} = '{encoded}'")
        
        return '\n'.join(header) + '\n\n'
    
    def obfuscate_file(self, input_path, output_path):
        """Obfuscate a single Python file"""
        with open(input_path, 'r') as f:
            code = f.read()
        
        print(f"🔒 Obfuscating {input_path}...")
        
        # Apply obfuscation techniques
        code = self.obfuscate_strings(code)
        code = self.obfuscate_variables(code)
        code = self.obfuscate_functions(code)
        code = self.add_dummy_code(code)
        
        # Create final obfuscated code
        obfuscated = self.create_header() + code
        
        # Save obfuscated version
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(obfuscated)
        
        print(f"✅ Saved obfuscated version to {output_path}")
    
    def obfuscate_directory(self, input_dir, output_dir):
        """Obfuscate all Python files in directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        for py_file in input_path.rglob('*.py'):
            relative_path = py_file.relative_to(input_path)
            out_file = output_path / relative_path
            
            self.obfuscate_file(str(py_file), str(out_file))

def main():
    print("🛡️  AEGIS OS CODE OBFUSCATION SYSTEM")
    print("="*50)
    
    obfuscator = AegisObfuscator()
    
    # Obfuscate overlay scripts
    overlay_dir = "overlay/usr/local/bin"
    obfuscated_dir = "overlay-obfuscated/usr/local/bin"
    
    if os.path.exists(overlay_dir):
        obfuscator.obfuscate_directory(overlay_dir, obfuscated_dir)
    
    # Obfuscate test simulation
    if os.path.exists("test-simulation.py"):
        obfuscator.obfuscate_file("test-simulation.py", "test-simulation-obfuscated.py")
    
    print("\n✅ Code obfuscation complete!")
    print("🔒 Protected files saved with -obfuscated suffix")
    print("⚠️  Keep original files secure - distribute only obfuscated versions")

if __name__ == "__main__":
    main()
