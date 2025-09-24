#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRANSLATE1.PY - Smart Blocking Multi-Engine Translation (FIXED PATHS VERSION)
Cascade: Google → Bing → Lingva → translate-shell
Features: Smart blocking + Complete logging + TXT mapping files + Configurable sleep + BATCH PROCESSING
Repository structure: translate/py/translate1.py
"""

import os
import sys
import re
import time
import requests
import subprocess
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Get repository root (parent of py/)
REPO_ROOT = Path(__file__).parent.parent

SCRIPT_NAME = "translate1.py"
# Configurable sleep times
SLEEP_SHELL = 0.3  # For translate-shell
SLEEP_OTHER = 0.5  # For Google, Bing, Lingva
# Configurable pattern for scripts.txt
PATTERN = "[3]"  # Change to [2], [3], [4] for other scripts

# ========== NEW: BATCH PROCESSING CONFIG ==========
BATCH_SIZE = 5      # Process 5 files per batch for Google/Bing
BATCH_DELAY = 20    # 30 seconds delay between batches

# ========== UTILITY FUNCTIONS ==========

def read_my_tasks():
    """Read files assigned to this script from tl/scripts.txt"""
    try:
        scripts_file = REPO_ROOT / "tl" / "scripts.txt"
        with open(scripts_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = rf'======= script: {re.escape(PATTERN)} =======\n(.*?)(?=======|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            files_section = match.group(1)
            files = re.findall(r'\d+\.\s+(.+\.rpy)', files_section)
            return files
        return []
    except FileNotFoundError:
        print(f"❌ File {REPO_ROOT / 'tl' / 'scripts.txt'} not found!")
        return []
    except Exception as e:
        print(f"❌ Error reading scripts.txt: {e}")
        return []

def log_message(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {SCRIPT_NAME}: {message}")

class RateLimitError(Exception):
    pass

class TranslationError(Exception):
    pass

# ========== ENHANCED LOGGING SYSTEM ==========

class TranslationLogger:
    """Comprehensive logging system"""
    def __init__(self):
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_entries = []
        self.start_time = datetime.now()
        
        # Ensure output directories exist
        output_root = REPO_ROOT / "output_3"
        (output_root / "logs").mkdir(parents=True, exist_ok=True)
        (output_root / "mappings").mkdir(parents=True, exist_ok=True)
        (output_root / "id").mkdir(parents=True, exist_ok=True)
    
    def log_translation(self, text, translated, engine, success=True, error=None):
        """Log individual translation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'original': text,
            'translated': translated,
            'engine': engine,
            'success': success,
            'error': str(error) if error else None,
            'length_original': len(text),
            'length_translated': len(translated) if translated else 0
        }
        self.log_entries.append(entry)
    
    def save_session_log(self):
        """Save complete session log"""
        log_file = REPO_ROOT / "output_3" / "logs" / f"{SCRIPT_NAME.replace('.py', '')}_session_{self.session_id}.json"
        
        session_data = {
            'session_id': self.session_id,
            'script_name': SCRIPT_NAME,
            'pattern': PATTERN,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60,
            'total_translations': len(self.log_entries),
            'translations': self.log_entries
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Session log saved: {log_file}")
        return str(log_file)

# ========== CORE RENPY TRANSLATOR ==========

class RenPyTranslatorCore:
    """Enhanced Core RenPy translation logic with TXT mapping export"""
    
    def __init__(self, input_file, logger):
        self.input_file = Path(input_file)
        self.filename_base = self.input_file.stem
        self.tag_map = defaultdict(str)
        self.var_map = defaultdict(str)
        self.parentheses_map = defaultdict(str)  # For (smile) type mappings
        self.tag_counter = 1
        self.var_counter = 1
        self.paren_counter = 1
        self.logger = logger
        
        # Translation stats
        self.stats = {
            'success': 0,
            'failed': 0,
            'skipped_code': 0,
            'total_processed': 0
        }
        
        # RenPy keywords yang TIDAK boleh ditranslate
        self.skip_keywords = [
            'show ', 'scene ', 'play ', 'stop ', 'queue ',
            'image ', 'define ', 'transform ', 'screen ',
            'jump ', 'call ', 'return', 'menu:', 'if ',
            'python:', 'init ', 'label ', 'with ',
            'hide ', 'at ', 'as ', '$', 'pause',
            'nvl ', 'window ', 'voice ', 'sound ',
            'music ', 'audio ', 'renpy.', 'camera '
        ]

    def _protect_escapes(self, text):
        """Protect escape sequences during translation"""
        replacements = {
            '\\n': '<!NEWLINE!>',
            '\\t': '<!TAB!>',
            '\\"': '<!QUOTE!>',
            '\\\\': '<!BACKSLASH!>',
            '\\r': '<!CARRIAGE!>',
            '\\{': '<!LEFTBRACE!>',
            '\\}': '<!RIGHTBRACE!>'
        }
        protected = text
        for old, new in replacements.items():
            protected = protected.replace(old, new)
        return protected

    def _restore_escapes(self, text):
        """Restore escape sequences after translation"""
        replacements = {
            '<!NEWLINE!>': '\\n',
            '<!TAB!>': '\\t',
            '<!QUOTE!>': '\\"',
            '<!BACKSLASH!>': '\\\\',
            '<!CARRIAGE!>': '\\r',
            '<!LEFTBRACE!>': '\\{',
            '<!RIGHTBRACE!>': '\\}'
        }
        restored = text
        for old, new in replacements.items():
            restored = restored.replace(old, new)
        restored = re.sub(r'\{\s+', '{', restored)
        restored = re.sub(r'\s+\}', '}', restored)
        return restored

    def _should_translate(self, line, text_match):
        """Check if text should be translated based on context"""
        before_quote = line[:text_match.start()].strip().lower()

        for keyword in self.skip_keywords:
            if before_quote.startswith(keyword.lower()):
                return False

        if '$' in before_quote:
            return False

        if before_quote.endswith(':'):
            return False

        if before_quote.endswith('old'):
            return False

        text_content = text_match.group(1)
        if (text_content.endswith(('.png', '.jpg', '.mp3', '.ogg', '.wav')) or
            '/' in text_content or '\\' in text_content):
            return False

        return True

    def _scan_tags_and_vars(self, content):
        """Scan and map tags, variables, and parentheses"""
        # Scan tags {i}, {/i}, etc.
        tag_pattern = r'\{([^{}]+)\}'
        for tag in set(re.findall(tag_pattern, content)):
            if tag not in self.tag_map:
                self.tag_map[tag] = str(self.tag_counter)
                self.tag_counter += 1
        
        # Scan variables [mname], [bname], etc.
        var_pattern = r'\[([^\[\]]+)\]'
        for var in set(re.findall(var_pattern, content)):
            if var not in self.var_map:
                self.var_map[var] = str(self.var_counter)
                self.var_counter += 1
        
        # Scan parentheses (smile), (angry), etc.
        paren_pattern = r'\(([^()]+)\)'
        for paren in set(re.findall(paren_pattern, content)):
            # Only map parentheses that look like expressions, not regular text
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', paren):  # Simple identifier pattern
                if paren not in self.parentheses_map:
                    self.parentheses_map[paren] = str(self.paren_counter)
                    self.paren_counter += 1

    def _translate_single_text(self, text, translate_function, line_num=0):
        """Wrapper to handle single text translation with logging"""
        self.stats['total_processed'] += 1

        if not text or not text.strip():
            return text

        # Protect escape sequences
        protected_text = self._protect_escapes(text)

        try:
            translated = translate_function(protected_text)
            
            if not translated or translated == protected_text:
                self.stats['failed'] += 1
                return text
                
            # Restore escape sequences
            final_text = self._restore_escapes(translated)
            self.stats['success'] += 1
            return final_text
            
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            self.stats['failed'] += 1
            return text

    def _process_line(self, line, translate_function, line_num):
        """Process single line with translation function"""
        original_line = line.rstrip()
        if (not original_line.strip() or 
            original_line.strip().startswith('#') or
            original_line.strip().startswith('$')):
            return line

        processed_line = original_line
        
        # Replace variables with placeholders
        processed_line = re.sub(
            r'\[([^\[\]]+)\]', 
            lambda m: f"[{self.var_map.get(m.group(1), '?')}]", 
            processed_line
        )
        
        # Replace tags with placeholders
        processed_line = re.sub(
            r'\{([^{}]+)\}', 
            lambda m: f"{{{self.tag_map.get(m.group(1), '?')}}}", 
            processed_line
        )
        
        # Replace parentheses with placeholders
        processed_line = re.sub(
            r'\(([^()]+)\)',
            lambda m: f"({self.parentheses_map.get(m.group(1), m.group(1))})",
            processed_line
        )
        
        # Replace dash characters
        processed_line = processed_line.replace('-', '©')
        processed_line = processed_line.replace('–', '®')
        processed_line = processed_line.replace('—', '™')

        def smart_translate_match(match):
            text = match.group(1)
            if not self._should_translate(processed_line, match):
                self.stats['skipped_code'] += 1
                return f'"{text}"'
            translated = self._translate_single_text(text, translate_function, line_num)
            return f'"{translated}"'

        final_line = re.sub(r'"([^"]*)"', smart_translate_match, processed_line)
        return final_line + '\n'

    def save_mappings(self):
        """Save tag and variable mappings to TXT file"""
        mapping_file = REPO_ROOT / "output_3" / "mappings" / f"{self.filename_base}_mapping.txt"
        
        with open(mapping_file, 'w', encoding='utf-8') as f:
            # Write tag mappings
            if self.tag_map:
                f.write("=== TAG MAPPING ===\n")
                for original, mapped in sorted(self.tag_map.items(), key=lambda x: int(x[1])):
                    f.write(f"{{{mapped}}} = {{{original}}}\n")
                f.write("\n")
            
            # Write variable mappings
            if self.var_map:
                f.write("=== VARIABLE MAPPING ===\n")
                for original, mapped in sorted(self.var_map.items(), key=lambda x: int(x[1])):
                    f.write(f"[{mapped}] = [{original}]\n")
                f.write("\n")
            
            # Write parentheses mappings
            if self.parentheses_map:
                f.write("=== KURUNG MAPPING ===\n")
                for original, mapped in sorted(self.parentheses_map.items(), key=lambda x: int(x[1])):
                    f.write(f"({mapped}) = ({original})\n")
        
        print(f"🗺️ Mappings saved: {mapping_file}")
        return str(mapping_file)

    def process_file(self, translate_function):
        """Process single file with provided translate function"""
        print(f"🔸 Processing {self.filename_base}...")
        
        if not self.input_file.exists():
            print(f"❌ File not found: {self.input_file}")
            return None
        
        try:
            # Read file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines(True)
            
            # Scan tags, variables, and parentheses
            self._scan_tags_and_vars(content)
            print(f"📋 Found {len(self.tag_map)} tags, {len(self.var_map)} variables, {len(self.parentheses_map)} parentheses")
            
            # Save mappings
            mapping_file = self.save_mappings()
            
            # Process each line
            results = []
            total_lines = len(lines)
            
            for i, line in enumerate(lines, 1):
                processed = self._process_line(line, translate_function, i)
                results.append(processed)
                
                # Progress update
                if i % 50 == 0 or i == total_lines:
                    percent = (i / total_lines) * 100
                    success_rate = (self.stats['success'] / max(1, self.stats['total_processed'])) * 100
                    print(f"  {percent:.0f}% | {i}/{total_lines} | Success: {success_rate:.0f}%")
            
            output_content = ''.join(results)
            
            print(f"✅ {self.filename_base} completed!")
            print(f"   Success: {self.stats['success']} | Failed: {self.stats['failed']} | Skipped: {self.stats['skipped_code']}")
            
            return {
                'filename': self.filename_base,
                'content': output_content,
                'stats': self.stats.copy(),
                'mapping_file': mapping_file
            }
            
        except Exception as e:
            print(f"❌ Error processing {self.filename_base}: {e}")
            return None

# ========== FREE TRANSLATION ENGINES ==========

class GoogleEngine:
    """Google Translate (using googletrans library)"""
    def __init__(self, logger):
        self.name = "Google"
        self.logger = logger
    
    def translate(self, text):
        """Translate using googletrans"""
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src='en', dest='id')
            
            if not result or not result.text:
                raise TranslationError("Empty Google translation result")
            
            # Log successful translation
            self.logger.log_translation(text, result.text, self.name, True)
            
            # Add configurable sleep
            time.sleep(SLEEP_OTHER)
            
            return result.text
            
        except ImportError:
            error = "googletrans library not installed. Run: pip install googletrans==4.0.0rc1"
            self.logger.log_translation(text, "", self.name, False, error)
            raise TranslationError(error)
        except Exception as e:
            self.logger.log_translation(text, "", self.name, False, e)
            if "rate limit" in str(e).lower():
                raise RateLimitError(f"Google rate limit: {e}")
            else:
                raise TranslationError(f"Google translate error: {e}")

class BingEngine:
    """Bing Translator (web scraping)"""
    def __init__(self, logger):
        self.name = "Bing"
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'
        })
    
    def translate(self, text):
        """Translate using Bing web interface"""
        try:
            url = "https://www.bing.com/ttranslatev3"
            data = {
                'text': text,
                'fromLang': 'en',
                'toLang': 'id',
            }
            
            response = self.session.post(url, data=data, timeout=20)
            
            if response.status_code == 429:
                error = "Bing rate limit exceeded"
                self.logger.log_translation(text, "", self.name, False, error)
                raise RateLimitError(error)
            elif response.status_code != 200:
                error = f"Bing HTTP error: {response.status_code}"
                self.logger.log_translation(text, "", self.name, False, error)
                raise TranslationError(error)
            
            # Parse Bing response (simplified)
            result = response.json()
            
            if 'translationResponse' in result:
                translated = result['translationResponse']
                self.logger.log_translation(text, translated, self.name, True)
                
                # Add configurable sleep
                time.sleep(SLEEP_OTHER)
                
                return translated
            else:
                error = "Bing response format changed"
                self.logger.log_translation(text, "", self.name, False, error)
                raise TranslationError(error)
                
        except requests.RequestException as e:
            error = f"Bing network error: {e}"
            self.logger.log_translation(text, "", self.name, False, error)
            raise TranslationError(error)
        except ValueError as e:
            error = f"Bing JSON parse error: {e}"
            self.logger.log_translation(text, "", self.name, False, error)
            raise TranslationError(error)

class LingvaEngine:
    """Lingva Translate (Google Translate proxy)"""
    def __init__(self, logger):
        self.name = "Lingva"
        self.logger = logger
        # Multiple Lingva instances
        self.endpoints = [
            "https://lingva.ml/api/v1/en/id",
            "https://translate.plausibility.cloud/api/v1/en/id",
            "https://lingva.lunar.icu/api/v1/en/id"
        ]
        self.current_endpoint = 0
    
    def translate(self, text):
        """Translate using Lingva API"""
        for attempt in range(len(self.endpoints)):
            try:
                endpoint = self.endpoints[self.current_endpoint]
                
                data = {'q': text}
                response = requests.post(endpoint, json=data, timeout=20)
                
                if response.status_code == 429:
                    error = "Lingva rate limit exceeded"
                    raise RateLimitError(error)
                elif response.status_code != 200:
                    error = f"Lingva HTTP {response.status_code}"
                    raise TranslationError(error)
                
                result = response.json()
                
                if 'translation' in result:
                    translated = result['translation']
                    self.logger.log_translation(text, translated, self.name, True)
                    
                    # Add configurable sleep
                    time.sleep(SLEEP_OTHER)
                    
                    return translated
                else:
                    error = "Lingva response missing translation field"
                    raise TranslationError(error)
                
            except (RateLimitError, TranslationError) as e:
                # Try next endpoint
                self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
                if attempt == len(self.endpoints) - 1:
                    self.logger.log_translation(text, "", self.name, False, e)
                    raise e
                continue
            except Exception as e:
                error = f"Lingva error: {e}"
                self.logger.log_translation(text, "", self.name, False, error)
                raise TranslationError(error)

class ShellEngine:
    """translate-shell (offline backup)"""
    def __init__(self, logger):
        self.name = "Shell"
        self.logger = logger
    
    def translate(self, text):
        """Translate using translate-shell"""
        try:
            # Escape text for shell
            escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
            cmd = f'trans -brief -no-ansi en:id "{escaped_text}"'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=25,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                error = f"translate-shell failed: {result.stderr}"
                self.logger.log_translation(text, "", self.name, False, error)
                raise TranslationError(error)
            
            translated = result.stdout.strip()
            if not translated:
                error = "Empty translation result"
                self.logger.log_translation(text, "", self.name, False, error)
                raise TranslationError(error)
            
            self.logger.log_translation(text, translated, self.name, True)
            
            # Add configurable sleep for shell (shorter)
            time.sleep(SLEEP_SHELL)
            
            return translated
            
        except subprocess.TimeoutExpired:
            error = "translate-shell timeout"
            self.logger.log_translation(text, "", self.name, False, error)
            raise TranslationError(error)
        except Exception as e:
            error = f"translate-shell error: {e}"
            self.logger.log_translation(text, "", self.name, False, error)
            raise TranslationError(error)

# ========== SMART MULTI-ENGINE PROCESSOR ==========

class SmartMultiEngineTranslator:
    """Smart cascade translation with engine blocking and enhanced logging"""
    
    def __init__(self, logger):
        self.logger = logger
        
        # Engine cascade configuration
        self.engines = [
            GoogleEngine(logger),
            BingEngine(logger),
            LingvaEngine(logger),
            ShellEngine(logger)
        ]
        
        # Smart blocking system
        self.blocked_engines = set()
        self.failure_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
        
        # NEW: Batch processing tracking
        self.files_processed = 0
        self.batch_number = 1
        
        # Statistics
        self.stats = {
            'google': 0,
            'bing': 0,
            'lingva': 0,
            'shell': 0,
            'failed': 0,
            'blocked_saves': 0,
            'batch_delays': 0  # NEW: Track batch delays
        }
    
    def _get_active_engines(self):
        """Get list of non-blocked engines"""
        return [e for e in self.engines if e.name not in self.blocked_engines]
    
    def _should_block_engine(self, engine_name):
        """Check if engine should be blocked based on failure rate"""
        failures = self.failure_counts[engine_name]
        successes = self.success_counts[engine_name]
        total = failures + successes
        
        # Block after 3 consecutive failures, or success rate < 20% after 5 attempts
        if failures >= 3 and successes == 0:
            return True
        elif total >= 5 and successes / total < 0.2:
            return True
        return False
    
    def translate_single(self, text):
        """Translate single text with smart blocking cascade"""
        if not text or not text.strip():
            return text
        
        active_engines = self._get_active_engines()
        
        if not active_engines:
            log_message("❌ All engines blocked! Resetting...")
            # Reset blocking if all engines are blocked
            self.blocked_engines.clear()
            self.failure_counts.clear()
            active_engines = self.engines
        
        # Count blocked engine saves
        blocked_count = len(self.engines) - len(active_engines)
        if blocked_count > 0:
            self.stats['blocked_saves'] += blocked_count
        
        for engine in active_engines:
            try:
                translated = engine.translate(text)
                
                # Success - update stats
                self.success_counts[engine.name] += 1
                self.failure_counts[engine.name] = 0  # Reset failure count
                
                engine_key = engine.name.lower()
                self.stats[engine_key] += 1
                
                # Enhanced logging with engine info
                if self.stats[engine_key] == 1 or self.stats[engine_key] % 50 == 0:
                    sleep_time = SLEEP_SHELL if engine.name == "Shell" else SLEEP_OTHER
                    log_message(f"✅ {engine.name} working ({self.stats[engine_key]} translations) [sleep: {sleep_time}s]")
                
                return translated
                
            except RateLimitError:
                log_message(f"⚠️ {engine.name} rate limited")
                self.failure_counts[engine.name] += 1
                
                # Check if should block
                if self._should_block_engine(engine.name):
                    self.blocked_engines.add(engine.name)
                    log_message(f"🚫 {engine.name} blocked due to rate limits")
                
                continue
                
            except TranslationError as e:
                self.failure_counts[engine.name] += 1
                
                # Check if should block
                if self._should_block_engine(engine.name):
                    self.blocked_engines.add(engine.name)
                    log_message(f"🚫 {engine.name} blocked after failures: {e}")
                
                continue
                
            except Exception as e:
                log_message(f"❌ {engine.name} unexpected error: {e}")
                self.failure_counts[engine.name] += 1
                continue
        
        # All active engines failed
        log_message("❌ All active engines failed for this text!")
        self.stats['failed'] += 1
        return text
    
    def handle_file_completed(self):
        """NEW: Handle file completion and batch logic for Google/Bing"""
        self.files_processed += 1
        
        # Check if we need batch delay for Google/Bing
        if self.files_processed % BATCH_SIZE == 0:
            # Check if Google or Bing are still active (not blocked)
            active_batch_engines = [e.name for e in self.engines 
                                  if e.name not in self.blocked_engines 
                                  and e.name in ['Google', 'Bing']]
            
            if active_batch_engines:
                log_message(f"📦 Batch {self.batch_number} completed ({BATCH_SIZE} files)")
                log_message(f"⏳ Cooling down {active_batch_engines} engines for {BATCH_DELAY}s...")
                
                time.sleep(BATCH_DELAY)
                self.stats['batch_delays'] += 1
                
                self.batch_number += 1
                log_message(f"🔄 Starting batch {self.batch_number}")
    
    def print_stats(self):
        """Print comprehensive statistics"""
        total_attempts = sum(v for k, v in self.stats.items() if k not in ['blocked_saves', 'batch_delays'])
        
        if total_attempts == 0:
            return
        
        log_message("📊 Smart Engine Statistics:")
        log_message(f"⏰ Sleep Configuration: Shell={SLEEP_SHELL}s, Others={SLEEP_OTHER}s")
        log_message(f"📦 Batch Configuration: {BATCH_SIZE} files/batch, {BATCH_DELAY}s delay")
        log_message(f"🎯 Pattern: {PATTERN}")
        
        # NEW: Batch statistics
        if self.stats['batch_delays'] > 0:
            log_message(f"📦 Batch delays executed: {self.stats['batch_delays']} (saved Google/Bing from rate limits)")
        
        # Engine usage
        for engine in ['google', 'bing', 'lingva', 'shell']:
            count = self.stats[engine]
            if count > 0:
                percentage = (count / total_attempts) * 100
                batch_info = " (BATCH ENGINE)" if engine in ['google', 'bing'] else ""
                log_message(f"  {engine.title()}: {count} texts ({percentage:.1f}%){batch_info}")
        
        # Failed translations
        failed = self.stats['failed']
        if failed > 0:
            percentage = (failed / total_attempts) * 100
            log_message(f"  Failed: {failed} texts ({percentage:.1f}%)")
        
        # Blocking efficiency
        blocked_saves = self.stats['blocked_saves']
        if blocked_saves > 0:
            log_message(f"  Blocked engine saves: {blocked_saves} unnecessary calls")
        
        # Currently blocked engines
        if self.blocked_engines:
            log_message(f"  Currently blocked: {', '.join(self.blocked_engines)}")
        
        # Success rates
        log_message("📈 Engine Performance:")
        for engine_name in ['Google', 'Bing', 'Lingva', 'Shell']:
            successes = self.success_counts[engine_name]
            failures = self.failure_counts[engine_name]
            total = successes + failures
            
            if total > 0:
                success_rate = (successes / total) * 100
                status = "🚫 BLOCKED" if engine_name in self.blocked_engines else "✅ Active"
                log_message(f"  {engine_name}: {success_rate:.1f}% success ({successes}/{total}) {status}")

# ========== ENHANCED FILE PROCESSING ==========

def process_files(file_list, translate_function, translator):
    """Process multiple files with comprehensive logging and batch management"""
    print(f"🚀 Processing {len(file_list)} files...")
    
    # NEW: Calculate expected batch delays
    expected_batches = len(file_list) // BATCH_SIZE
    if expected_batches > 0:
        total_batch_time = expected_batches * BATCH_DELAY
        log_message(f"📦 Expected {expected_batches} batch delays, ~{total_batch_time}s total delay time")
    
    results = []
    
    for filename in file_list:
        filepath = REPO_ROOT / "tl" / filename
        logger = TranslationLogger()
        renpy_translator = RenPyTranslatorCore(filepath, logger)
        
        result = renpy_translator.process_file(translate_function)
        
        if result:
            # Save translated file to output_tl/id/
            output_filename = REPO_ROOT / "output_3" / "id" / f"{result['filename']}_translated.rpy"
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(result['content'])
                
            print(f"💾 Saved: {output_filename}")
            
            # Save session log
            log_file = logger.save_session_log()
            result['log_file'] = log_file
            
            results.append(result)
        
        # NEW: Handle batch completion after each file
        translator.handle_file_completed()
        
        print("-" * 50)
    
    print(f"🎉 Batch completed! {len(results)}/{len(file_list)} files processed successfully.")
    return results

# ========== MAIN EXECUTION ==========

def main():
    """Main execution function"""
    log_message("🚀 Starting smart multi-engine translation pipeline...")
    log_message("🧠 Smart blocking enabled: Failed engines will be skipped")
    log_message("📝 Complete logging: TXT mappings + Session logs will be saved")
    log_message(f"⏰ Sleep config: Shell={SLEEP_SHELL}s, Others={SLEEP_OTHER}s")
    log_message(f"📦 Batch config: Google/Bing process {BATCH_SIZE} files → {BATCH_DELAY}s delay")
    log_message(f"🎯 Processing pattern: {PATTERN}")
    
    # Read assigned files from tl/scripts.txt
    my_files = read_my_tasks()
    log_message(f"📋 Found {len(my_files)} assigned files: {my_files}")
    
    if not my_files:
        log_message(f"⚪ No files assigned to pattern {PATTERN}")
        return
    
    # Check if files exist
    existing_files = []
    for filename in my_files:
        filepath = REPO_ROOT / "tl" / filename
        if filepath.exists():
            existing_files.append(filename)
        else:
            log_message(f"⚠️ File not found: {filepath}")
    
    if not existing_files:
        log_message("❌ No valid files found!")
        return
    
    log_message(f"✅ Processing {len(existing_files)} valid files...")
    
    # Initialize smart multi-engine translator with logger
    session_logger = TranslationLogger()
    translator = SmartMultiEngineTranslator(session_logger)
    
    # Process files using smart blocking logic with batch management
    try:
        results = process_files(existing_files, translator.translate_single, translator)
        
        # Print comprehensive statistics
        translator.print_stats()
        
        if results:
            log_message(f"🎉 {SCRIPT_NAME} completed successfully!")
            log_message(f"   Pattern: {PATTERN}")
            log_message(f"   Processed: {len(results)} files in {translator.batch_number} batches")
            log_message(f"   Batch delays used: {translator.stats['batch_delays']}")
            log_message("📁 Generated files:")
            for result in results:
                log_message(f"   - Translation: output_3/id/{result['filename']}_translated.rpy")
                log_message(f"   - Mappings: {result['mapping_file']}")
                if 'log_file' in result:
                    log_message(f"   - Log: {result['log_file']}")
        else:
            log_message("❌ No files were processed successfully")
            
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()