"""
ULTIMATE DANK MEMER BOT - AUTO-DISABLE ON VERIFICATION
Features:
• Auto-disables account when verification detected
• Sets state to false in config.json
• Stops all workers for disabled account
• Multi-account support
• Fixed trivia auto-recording
• New tidy system
• Random postmemes selection
• NEW: Simple auto-use items system (no checks, just uses)
"""

import json
import asyncio
import aiohttp
import time
import random
import re
import hashlib
import sys
import os
from asyncio import Lock
from typing import List, Dict, Tuple, Optional

# ============================================================================
# TRIVIA SOLVER - WITH AUTO-RECORDER
# ============================================================================
class TriviaSolver:
    """FIXED: Actually reads trivia.json from your folder + AUTO-RECORDS new answers"""
    
    def __init__(self):
        self.trivia_data = {}
        self.new_answers = 0
        self.load_trivia_data()
        
    def load_trivia_data(self):
        """Load trivia.json with answers"""
        try:
            if not os.path.exists('trivia.json'):
                print("❌ trivia.json file NOT FOUND, creating new one...")
                self.trivia_data = {}
                with open('trivia.json', 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
                return
            
            print(f"✅ Found trivia.json at: {os.path.abspath('trivia.json')}")
            
            with open('trivia.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, dict):
                    self.trivia_data = data
                    print(f"✅ Loaded {len(self.trivia_data)} trivia questions from database")
                    if self.trivia_data:
                        sample_keys = list(self.trivia_data.keys())[:2]
                        for key in sample_keys:
                            print(f"📊 Sample: {key[:50]}... -> {self.trivia_data[key][:30]}...")
                else:
                    print("❌ trivia.json is not in correct format (should be dict)")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in trivia.json: {e}")
        except Exception as e:
            print(f"❌ Error loading trivia.json: {e}")
    
    def find_answer(self, question: str) -> str:
        """Find answer for trivia question"""
        if not self.trivia_data:
            return ""
        
        clean_question = question.strip()
        clean_question = re.sub(r'\*\*|\*|`', '', clean_question)
        
        if clean_question in self.trivia_data:
            return self.trivia_data[clean_question]
        
        question_lower = clean_question.lower()
        for q, a in self.trivia_data.items():
            if q.lower() == question_lower:
                return a
        
        for q, a in self.trivia_data.items():
            if q in clean_question or clean_question in q:
                return a
        
        question_words = set(question_lower.split())
        for q, a in self.trivia_data.items():
            q_words = set(q.lower().split())
            if len(question_words.intersection(q_words)) >= 3:
                return a
        
        return ""
    
    def save_answer(self, question: str, answer: str):
        """Save a new question-answer pair to trivia.json"""
        clean_question = question.strip()
        clean_question = re.sub(r'\*\*|\*|`', '', clean_question)
        
        if clean_question in self.trivia_data:
            if self.trivia_data[clean_question] == answer:
                return False
            else:
                print(f"🔄 Updating answer for existing question")
        
        self.trivia_data[clean_question] = answer
        self.new_answers += 1
        
        try:
            with open('trivia.json', 'w', encoding='utf-8') as f:
                json.dump(self.trivia_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved new answer to database: {answer}")
            print(f"   Question: {clean_question[:80]}...")
            return True
        except Exception as e:
            print(f"❌ Failed to save to trivia.json: {e}")
            return False
    
    def extract_correct_answer_from_response(self, response_text: str) -> str:
        """Extract correct answer from trivia response"""
        response_text = response_text.lower()
        
        if "the correct answer was" in response_text:
            after_was = response_text.split("the correct answer was")[1].strip()
            after_was = re.sub(r'\*\*|\*|`', '', after_was)
            match = re.match(r'^([^.,!?\n]+)', after_was)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def get_stats(self):
        """Get trivia statistics"""
        return {
            'total_questions': len(self.trivia_data),
            'new_answers_added': self.new_answers
        }

# ============================================================================
# PROFESSIONAL BLACKJACK SOLVER
# ============================================================================
class ProfessionalBlackjackSolver:
    def __init__(self):
        self.wins = 0
        self.losses = 0
        self.total_earnings = 0
    
    def extract_card_values(self, emoji_string: str) -> list:
        pattern = r'<:bjFace([0-9JQKA]+)[RB]:[0-9]+>'
        matches = re.findall(pattern, emoji_string)
        return matches if matches else []
    
    def calculate_hand_value(self, cards: list) -> tuple:
        total = 0
        has_ace = False
        ace_count = 0
        
        for card in cards:
            if card == 'A':
                total += 11
                ace_count += 1
                has_ace = True
            elif card in ['K', 'Q', 'J']:
                total += 10
            else:
                total += int(card)
        
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1
        
        return total, has_ace
    
    def make_decision(self, player_cards: list, dealer_cards: list, can_surrender: bool, can_double: bool, can_split: bool) -> int:
        player_sum, is_soft = self.calculate_hand_value(player_cards)
        if player_sum >= 17:
            return 1
        else:
            return 0
    
    def extract_net_value(self, description: str) -> int:
        pattern = r'Net:\s\*\*⏣ ([+\-]?[0-9,]+)\*\*'
        match = re.search(pattern, description)
        if not match:
            return 0
        value_str = match.group(1).replace(',', '')
        try:
            return int(value_str)
        except:
            return 0

# ============================================================================
# SMART SEARCH SOLVER
# ============================================================================
class SmartSearchSolver:
    def __init__(self):
        self.location_stats = {}
        self.priority_locations = ["dresser", "attic", "couch", "laundry", "coat", "pocket"]
        self.secondary_locations = ["mailbox", "discord", "sewer", "grass", "tree"]
        self.avoid_locations = ["bank", "manhole", "trash"]
    
    def analyze_message(self, message: dict) -> Tuple[List[str], Dict[str, float]]:
        if 'components' not in message:
            return [], {}
        
        buttons = message['components'][0]['components']
        available_locations = []
        location_scores = {}
        
        for btn in buttons:
            location = btn.get('label', '').lower()
            available_locations.append(location)
            
            score = 0
            if location in self.priority_locations:
                score += 100
            elif location in self.secondary_locations:
                score += 50
            elif location in self.avoid_locations:
                score -= 100
            else:
                score += 10
            
            location_scores[location] = score
        
        return available_locations, location_scores
    
    def choose_best_location(self, available_locations: List[str], location_scores: Dict[str, float]) -> str:
        if not available_locations:
            return ""
        
        best_location = max(location_scores, key=location_scores.get)
        return best_location
    
    def update_stats(self, location: str, success: bool):
        if location not in self.location_stats:
            self.location_stats[location] = {'attempts': 0, 'successes': 0}
        
        self.location_stats[location]['attempts'] += 1
        if success:
            self.location_stats[location]['successes'] += 1

# ============================================================================
# SMART CRIME SOLVER - FIXED TO SELECT BEST OPTION
# ============================================================================
class SmartCrimeSolver:
    def __init__(self):
        self.crime_stats = {}
        self.crime_rewards = {
            'hacking': {'min': 2000, 'max': 6000, 'risk': 0.5},
            'tax evasion': {'min': 1500, 'max': 4500, 'risk': 0.4},
            'fraud': {'min': 1000, 'max': 3500, 'risk': 0.3},
            'eating a hot dog sideways': {'min': 500, 'max': 2000, 'risk': 0.2},
            'trespassing': {'min': 800, 'max': 2500, 'risk': 0.35},
            'bank robbing': {'min': 5000, 'max': 15000, 'risk': 0.7},
            'murder': {'min': 3000, 'max': 9000, 'risk': 0.8},
            'stab grandma': {'min': 4000, 'max': 12000, 'risk': 0.75},
            'drug distribution': {'min': 2500, 'max': 7500, 'risk': 0.65},
            'littering': {'min': 300, 'max': 1000, 'risk': 0.1},
            'cyber bullying': {'min': 700, 'max': 2200, 'risk': 0.25},
        }
    
    def analyze_crime_options(self, message: dict) -> Tuple[List[str], Dict[str, float]]:
        if 'components' not in message:
            return [], {}
        
        buttons = message['components'][0]['components']
        available_crimes = []
        crime_scores = {}
        
        for btn in buttons:
            crime_name = btn.get('label', '').lower()
            available_crimes.append(crime_name)
            
            crime_data = self.crime_rewards.get(crime_name, {'min': 1000, 'max': 3000, 'risk': 0.5})
            avg_reward = (crime_data['min'] + crime_data['max']) / 2
            risk = crime_data['risk']
            
            expected_value = avg_reward * (1 - risk)
            score = expected_value
            
            crime_scores[crime_name] = score
        
        return available_crimes, crime_scores
    
    def choose_best_crime(self, available_crimes: List[str], crime_scores: Dict[str, float]) -> str:
        if not available_crimes or not crime_scores:
            return available_crimes[0] if available_crimes else ""
        
        print(f"📊 CRIME SCORES:")
        for crime, score in crime_scores.items():
            print(f"   {crime}: {score:.2f}")
        
        best_crime = max(crime_scores.items(), key=lambda x: x[1])[0]
        return best_crime
    
    def update_stats(self, crime_name: str, success: bool, reward: int = 0):
        if crime_name not in self.crime_stats:
            self.crime_stats[crime_name] = {'attempts': 0, 'successes': 0, 'total_reward': 0}
        
        self.crime_stats[crime_name]['attempts'] += 1
        if success:
            self.crime_stats[crime_name]['successes'] += 1
            self.crime_stats[crime_name]['total_reward'] += reward

# ============================================================================
# TIDY SOLVER - UPDATED WITH NEW BUTTON SYSTEM
# ============================================================================
class TidySolver:
    """Smart solver for Dank Memer tidy command - UPDATED"""
    
    def __init__(self):
        self.tool_priority = ["hand", "broom", "vacuum"]
        self.tool_stats = {}
    
    def choose_best_tool_pattern(self, available_tools: Dict[str, str]) -> str:
        """Choose the best available tool based on priority"""
        if not available_tools:
            return ""
        
        for tool_name in self.tool_priority:
            if tool_name in available_tools:
                return tool_name
        
        return list(available_tools.keys())[0] if available_tools else ""
    
    def update_stats(self, tool_name: str, success: bool, coins_earned: int = 0):
        """Track tool performance"""
        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = {
                'uses': 0,
                'successes': 0,
                'total_coins': 0
            }
        
        self.tool_stats[tool_name]['uses'] += 1
        if success:
            self.tool_stats[tool_name]['successes'] += 1
            self.tool_stats[tool_name]['total_coins'] += coins_earned

# ============================================================================
# POSTMEMES SOLVER - WITH RANDOM SELECTION
# ============================================================================
class PostmemesSolver:
    def __init__(self):
        self.stats = {
            'attempts': 0,
            'successes': 0,
            'platforms_used': {},
            'meme_types_used': {},
            'earnings': 0
        }
        
        self.last_platform = None
        self.last_meme_type = None
        self.repeat_count = 0
    
    def extract_dropdown_options(self, message: dict) -> Tuple[Dict[str, list], Dict[str, str]]:
        """Extract dropdown options from postmemes message"""
        if 'components' not in message:
            return {}, {}
        
        dropdowns = {}
        custom_ids = {}
        
        for row in message.get('components', []):
            for component in row.get('components', []):
                if component.get('type') == 3:
                    custom_id = component.get('custom_id', '')
                    options = component.get('options', [])
                    
                    if custom_id.endswith(':location'):
                        dropdowns['platform'] = options
                        custom_ids['platform'] = custom_id
                    
                    elif custom_id.endswith(':kind'):
                        dropdowns['meme_type'] = options
                        custom_ids['meme_type'] = custom_id
        
        return dropdowns, custom_ids
    
    def choose_random_selections(self, dropdowns: Dict[str, list]) -> Dict[str, str]:
        """Choose random platform and meme type"""
        selections = {}
        
        if 'platform' in dropdowns:
            available_platforms = [opt['value'] for opt in dropdowns['platform']]
            if available_platforms:
                if self.last_platform and self.repeat_count >= 2:
                    available_platforms = [p for p in available_platforms if p != self.last_platform]
                
                if available_platforms:
                    selections['platform'] = random.choice(available_platforms)
                    if selections['platform'] == self.last_platform:
                        self.repeat_count += 1
                    else:
                        self.repeat_count = 0
                    self.last_platform = selections['platform']
                else:
                    selections['platform'] = self.last_platform or random.choice([opt['value'] for opt in dropdowns['platform']])
        
        if 'meme_type' in dropdowns:
            available_types = [opt['value'] for opt in dropdowns['meme_type']]
            if available_types:
                selections['meme_type'] = random.choice(available_types)
                self.last_meme_type = selections['meme_type']
        
        return selections
    
    def update_stats(self, platform: str, meme_type: str, success: bool, coins_earned: int = 0):
        """Update statistics"""
        self.stats['attempts'] += 1
        if success:
            self.stats['successes'] += 1
            self.stats['earnings'] += coins_earned
        
        if platform not in self.stats['platforms_used']:
            self.stats['platforms_used'][platform] = 0
        self.stats['platforms_used'][platform] += 1
        
        if meme_type not in self.stats['meme_types_used']:
            self.stats['meme_types_used'][meme_type] = 0
        self.stats['meme_types_used'][meme_type] += 1

# ============================================================================
# SIMPLE AUTO USE SYSTEM - NO CHECKS, JUST USES
# ============================================================================
class SimpleAutoUse:
    """Simple auto-use system - just runs use command on loop"""
    
    def __init__(self):
        self.config = None
        self.item_timers = {}  # {"apple": {"last_used": timestamp, "delay": 86400}}
        self.stats = {}        # {"apple": {"uses": 0}}
    
    def load_config(self, config_data: dict):
        """Load auto-use configuration"""
        self.config = config_data.get('autoUse', {})
        if not self.config:
            print("⚠️ [AUTO-USE] No autoUse configuration found")
            return False
        
        if self.config.get('state', False):
            items = self.config.get('items', {})
            for item_name, item_config in items.items():
                if item_config.get('state', True):
                    self.item_timers[item_name] = {
                        'last_used': 0,
                        'delay': item_config.get('delay', 86400),
                        'quantity': item_config.get('quantity', 1)
                    }
                    self.stats[item_name] = {'uses': 0}
            
            print(f"✅ [AUTO-USE] Loaded {len(self.item_timers)} items for auto-use")
            return True
        return False
    
    def is_enabled(self):
        """Check if auto-use is enabled"""
        return self.config.get('state', False) if self.config else False
    
    def get_items_to_use(self):
        """Get items that are ready to use (delay expired)"""
        items_to_use = []
        current_time = time.time()
        
        for item_name, timer in self.item_timers.items():
            if current_time - timer['last_used'] >= timer['delay']:
                items_to_use.append({
                    'name': item_name,
                    'quantity': timer['quantity'],
                    'delay': timer['delay']
                })
        
        return items_to_use
    
    def update_timer(self, item_name: str):
        """Update last used time for an item"""
        if item_name in self.item_timers:
            self.item_timers[item_name]['last_used'] = time.time()
            self.stats[item_name]['uses'] += 1
    
    def get_next_use_time(self, item_name: str):
        """Get when next use will be"""
        if item_name not in self.item_timers:
            return "Not configured"
        
        timer = self.item_timers[item_name]
        next_use = timer['last_used'] + timer['delay']
        
        if timer['last_used'] == 0:
            return "Ready to use"
        
        if next_use <= time.time():
            return "Ready to use"
        
        time_until = next_use - time.time()
        
        # Format time
        if time_until > 3600:
            hours = int(time_until // 3600)
            minutes = int((time_until % 3600) // 60)
            return f"{hours}h {minutes}m"
        elif time_until > 60:
            minutes = int(time_until // 60)
            return f"{minutes}m"
        else:
            return f"{int(time_until)}s"
    
    def get_stats(self):
        """Get auto-use statistics"""
        total_uses = sum(stats['uses'] for stats in self.stats.values())
        
        return {
            'total_items': len(self.stats),
            'total_uses': total_uses,
            'items': self.stats
        }

# ============================================================================
# WORK MINIGAME SOLVER
# ============================================================================
class WorkMinigameSolver:
    async def solve_minigame(self, bot_instance, message: dict) -> bool:
        if not message.get('embeds'):
            return False
        
        if 'components' in message and message['components'][0]['components']:
            button = message['components'][0]['components'][0]
            return await bot_instance.click_button(message, button.get('label', ''))
        
        return False

# ============================================================================
# MAIN BOT CLASS - WITH AUTO-DISABLE ON VERIFICATION
# ============================================================================
class SmartDankBot:
    def __init__(self, token, channel_id, guild_id=None, account_index=0, config_path='config.json'):
        self.token = token
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.account_index = account_index
        self.config_path = config_path
        self.config = None
        
        self.session = None
        self.commands = self.load_commands()
        self.load_full_config()
        self.command_last_run = {}
        
        seed = f"{token}{channel_id}"
        self.session_id = hashlib.md5(seed.encode()).hexdigest()
        
        self.blackjack_solver = ProfessionalBlackjackSolver()
        self.search_solver = SmartSearchSolver()
        self.crime_solver = SmartCrimeSolver()
        self.tidy_solver = TidySolver()
        self.trivia_solver = TriviaSolver()
        self.postmemes_solver = PostmemesSolver()
        self.work_solver = WorkMinigameSolver()
        self.auto_use = SimpleAutoUse()
        
        # Load auto-use config
        if self.config and 'autoUse' in self.config:
            self.auto_use.load_config(self.config)
        
        self.global_lock = Lock()
        self.lock_owner = None
        self.currently_running = set()
        
        self.verification_required = False
        self.verification_detected_at = 0
        
        self.last_api_call = 0
        self.min_request_gap = 1.5
        
        print(f"🤖 Bot initialized for account {account_index}")
    
    def load_full_config(self):
        """Load the entire config file to access all accounts"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"❌ Error loading full config: {e}")
            self.config = {"accounts": []}
    
    def load_config_commands(self):
        """Load only command config"""
        try:
            return self.config.get('commands', {})
        except:
            return {}
    
    def get_account_state(self):
        """Check if this account is still enabled"""
        try:
            # Reload config to get latest state
            self.load_full_config()
            if (self.config and 'accounts' in self.config and 
                self.account_index < len(self.config['accounts'])):
                return self.config['accounts'][self.account_index].get('state', True)
        except Exception as e:
            print(f"⚠️ Error checking account state: {e}")
        return True
    
    def disable_current_account(self):
        """Disable this account in config.json and stop bot"""
        try:
            self.load_full_config()
            
            if not self.config or 'accounts' not in self.config:
                print("❌ Cannot disable account: Invalid config structure")
                return False
            
            if self.account_index < len(self.config['accounts']):
                self.config['accounts'][self.account_index]['state'] = False
                
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                print(f"\n" + "!"*60)
                print(f"🚫 ACCOUNT {self.account_index} DISABLED IN CONFIG.JSON")
                print(f"   Token: {self.token[:20]}...")
                print(f"   Channel: {self.channel_id}")
                print(f"   Config saved: {self.config_path}")
                print(f"!"*60)
                
                # Log the event
                self.log_verification_event("DISABLED")
                return True
            else:
                print(f"❌ Account index {self.account_index} out of range")
                return False
                
        except Exception as e:
            print(f"❌ Failed to disable account: {e}")
            return False
    
    def log_verification_event(self, action: str = "DETECTED"):
        """Log verification event to a file"""
        try:
            log_entry = {
                'timestamp': time.time(),
                'time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
                'account_index': self.account_index,
                'token_prefix': self.token[:20] + '...',
                'channel_id': self.channel_id,
                'guild_id': self.guild_id,
                'action': action
            }
            
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            # Append to log file
            with open('logs/verification_log.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
            print(f"📝 Logged verification event to logs/verification_log.json")
        except Exception as e:
            print(f"⚠️ Could not log verification event: {e}")
    
    async def check_and_handle_verification(self, response):
        """Enhanced verification handler that disables account"""
        if not self.has_verification_required(response):
            return False
        
        print(f"\n" + "!"*60)
        print(f"🚨 VERIFICATION REQUIRED DETECTED!")
        print(f"!"*60)
        
        if self.check_for_verification_buttons(response):
            print(f"📛 Trigger: Verification buttons found")
        if self.check_for_verification_embed(response):
            print(f"📛 Trigger: Verification embed detected")
        
        # Disable this account in config
        success = self.disable_current_account()
        
        if success:
            print(f"✅ Account {self.account_index} has been DISABLED")
            print(f"⛔ All workers will stop for this account")
        
        self.verification_required = True
        self.verification_detected_at = time.time()
        
        return True
    
    def load_commands(self):
        try:
            with open('dank_commands.json', 'r') as f:
                commands = json.load(f)
                return {cmd['name'].lower(): cmd for cmd in commands}
        except Exception as e:
            print(f"❌ Error loading commands: {e}")
            return {}
    
    def get_command_cooldown(self, command_name: str, default: int) -> int:
        """Get cooldown for a command from config"""
        try:
            cmd_config = self.config.get('commands', {}).get(command_name, {})
            if 'delay' in cmd_config:
                return cmd_config['delay']
            elif 'cooldown' in cmd_config:
                return cmd_config['cooldown']
        except:
            pass
        return default
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def wait_rate_limit(self):
        now = time.time()
        if now - self.last_api_call < self.min_request_gap:
            wait_time = self.min_request_gap - (now - self.last_api_call)
            await asyncio.sleep(wait_time)
        self.last_api_call = time.time()
    
    async def acquire_lock(self, command_name: str):
        if not self.global_lock.locked():
            self.lock_owner = command_name
            await self.global_lock.acquire()
            self.currently_running.add(command_name)
            return True
        return False
    
    async def release_lock(self):
        if self.global_lock.locked():
            if self.lock_owner:
                self.currently_running.discard(self.lock_owner)
            self.lock_owner = None
            self.global_lock.release()
    
    async def wait_for_lock(self, command_name: str, timeout: int = 10):
        if self.global_lock.locked():
            print(f"⏸️ [{command_name}] Waiting for {self.lock_owner} to finish...")
            try:
                await asyncio.wait_for(self.global_lock.acquire(), timeout=timeout)
                self.global_lock.release()
                print(f"✅ [{command_name}] Lock released, continuing...")
            except asyncio.TimeoutError:
                print(f"⚠️ [{command_name}] Lock timeout, proceeding anyway")
    
    # ============================================================================
    # VERIFICATION DETECTION
    # ============================================================================
    
    def check_for_verification_buttons(self, message_data: dict) -> bool:
        """Check if message contains verification buttons"""
        if not message_data or 'components' not in message_data:
            return False
        
        for row in message_data.get('components', []):
            for component in row.get('components', []):
                if component.get('type') == 2:
                    label = component.get('label', '').lower()
                    if any(keyword in label for keyword in ['verify', 'verification', 'captcha', 'pass verification', 'human', 'robot']):
                        return True
        
        return False
    
    def check_for_verification_embed(self, message_data: dict) -> bool:
        """Check if message contains verification embed"""
        if not message_data or 'embeds' not in message_data:
            return False
        
        for embed in message_data.get('embeds', []):
            description = embed.get('description', '').lower()
            title = embed.get('title', '').lower()
            
            if any(keyword in description or keyword in title 
                  for keyword in ['verification', 'captcha', 'verify', 'human', 'robot', 'suspicious', 'security']):
                return True
        
        return False
    
    def has_verification_required(self, message_data: dict) -> bool:
        """Check if message indicates verification is required"""
        return (self.check_for_verification_buttons(message_data) or 
                self.check_for_verification_embed(message_data))
    
    # ============================================================================
    # BUTTON METHODS
    # ============================================================================
    
    def extract_button(self, message, pattern):
        """Extract button ID using regex pattern matching"""
        msg_str = json.dumps(message)
        regex = f'"custom_id"\\s*:\\s*"([^"]*{re.escape(pattern)}[^"]*)"'
        match = re.search(regex, msg_str)
        if match:
            return match.group(1)
        
        regex2 = f'"custom_id":"([^"]*)"[^}}]*"label":"[^"]*{re.escape(pattern)}[^"]*"'
        match2 = re.search(regex2, msg_str)
        return match2.group(1) if match2 else None
    
    async def click_button_new(self, message_id, custom_id):
        """Click button with message_flags (for tidy)"""
        await self.wait_rate_limit()
        
        try:
            seed = f"{self.token}{self.channel_id}{int(time.time())}"
            session_id = hashlib.md5(seed.encode()).hexdigest()
            
            payload = {
                "type": 3,
                "nonce": str(int(time.time() * 1000)),
                "channel_id": self.channel_id,
                "message_id": message_id,
                "session_id": session_id,
                "application_id": "270904126974590976",
                "data": {
                    "component_type": 2,
                    "custom_id": custom_id
                },
                "message_flags": 32768
            }
            
            if self.guild_id:
                payload["guild_id"] = self.guild_id
            
            async with self.session.post(
                "https://discord.com/api/v9/interactions",
                json=payload,
                timeout=10
            ) as resp:
                return resp.status == 204
                
        except Exception as e:
            print(f"❌ New button click error: {e}")
            return False
    
    async def select_dropdown(self, message_id: str, custom_id: str, values: List[str]) -> bool:
        """Select options from a dropdown menu"""
        await self.wait_rate_limit()
        
        try:
            seed = f"{self.token}{self.channel_id}{int(time.time())}"
            session_id = hashlib.md5(seed.encode()).hexdigest()
            
            payload = {
                "type": 3,
                "nonce": str(int(time.time() * 1000)),
                "channel_id": self.channel_id,
                "message_id": message_id,
                "session_id": session_id,
                "application_id": "270904126974590976",
                "data": {
                    "component_type": 3,
                    "custom_id": custom_id,
                    "values": values
                },
                "message_flags": 32768
            }
            
            if self.guild_id:
                payload["guild_id"] = self.guild_id
            
            async with self.session.post(
                "https://discord.com/api/v9/interactions",
                json=payload,
                timeout=10
            ) as resp:
                return resp.status == 204
                
        except Exception as e:
            print(f"❌ Dropdown selection error: {e}")
            return False
    
    async def click_button(self, message_data: dict, button_label: str = None) -> bool:
        """ORIGINAL: Click button by label (for search, crime, etc.)"""
        await self.wait_rate_limit()
        
        try:
            target_btn = None
            for row in message_data.get('components', []):
                for btn in row.get('components', []):
                    if btn.get('type') == 2:
                        if button_label:
                            if btn.get('label', '').lower() == button_label.lower():
                                target_btn = btn
                                break
                        else:
                            target_btn = btn
                            break
                if target_btn:
                    break
            
            if not target_btn:
                return False
            
            payload = {
                "type": 3,
                "nonce": str(int(time.time() * 1000)),
                "guild_id": message_data.get('guild_id', self.guild_id),
                "channel_id": self.channel_id,
                "message_id": message_data['id'],
                "session_id": self.session_id,
                "application_id": "270904126974590976",
                "data": {"component_type": 2, "custom_id": target_btn['custom_id']}
            }
            
            async with self.session.post(
                "https://discord.com/api/v9/interactions",
                json=payload,
                timeout=10
            ) as resp:
                return resp.status == 204
        except:
            return False
    
    async def send_command(self, command_name: str, **kwargs) -> bool:
        """Send command and return success"""
        await self.wait_rate_limit()
        
        cmd_data = self.commands.get(command_name.lower())
        if not cmd_data:
            print(f"❌ Command '{command_name}' not found in dank_commands.json")
            return False
        
        payload = {
            "type": 2,
            "application_id": "270904126974590976",
            "channel_id": self.channel_id,
            "session_id": self.session_id,
            "nonce": str(int(time.time() * 1000)),
            "data": {
                "version": cmd_data.get('version', '1'),
                "id": cmd_data['id'],
                "name": cmd_data['name'],
                "type": 1
            }
        }
        
        if kwargs.get('subcommand'):
            payload["data"]["options"] = [{
                "type": 1,
                "name": kwargs['subcommand'],
                "options": kwargs.get('options', [])
            }]
        elif kwargs.get('bet'):
            payload["data"]["options"] = [{
                "type": 3,
                "name": "bet",
                "value": kwargs['bet']
            }]
        elif kwargs.get('amount'):
            payload["data"]["options"] = [{
                "type": 3,
                "name": "amount",
                "value": kwargs['amount']
            }]
        elif kwargs.get('item'):
            payload["data"]["options"] = [{
                "type": 3,
                "name": "item",
                "value": kwargs['item']
            }]
            if kwargs.get('quantity', 1) > 1:
                payload["data"]["options"].append({
                    "type": 4,
                    "name": "quantity",
                    "value": kwargs['quantity']
                })
        
        if self.guild_id:
            payload["guild_id"] = self.guild_id
        
        try:
            async with self.session.post(
                "https://discord.com/api/v9/interactions",
                json=payload,
                timeout=10
            ) as resp:
                if resp.status == 204:
                    return True
                else:
                    if resp.status == 429:
                        error_text = await resp.text()
                        retry_match = re.search(r'"retry_after":\s*([0-9.]+)', error_text)
                        if retry_match:
                            retry_time = float(retry_match.group(1))
                            print(f"⏳ Rate limited! Waiting {retry_time}s...")
                            await asyncio.sleep(retry_time)
                            return False
                    print(f"❌ Command failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ Network error: {e}")
            return False
    
    async def get_messages(self, limit=10):
        """Get recent messages from channel"""
        try:
            async with self.session.get(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages?limit={limit}",
                timeout=5
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
        return []
    
    async def monitor_for_response(self, timeout: int = 8) -> dict:
        """Monitor for Dank Memer response"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                await self.wait_rate_limit()
                messages = await self.get_messages(limit=10)
                
                for msg in messages:
                    if msg.get('author', {}).get('id') == '270904126974590976':
                        return msg
            except Exception as e:
                print(f"❌ Error in monitor_for_response: {e}")
            
            await asyncio.sleep(0.5)
        
        return None
    
    # ============================================================================
    # WORKER METHODS WITH AUTO-DISABLE CHECK
    # ============================================================================
    
    async def search_worker(self):
        """Smart Search Worker with auto-disable"""
        print("👷 Smart Search Worker started")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [SEARCH] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [SEARCH] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get('search', 0)
                cooldown = self.get_command_cooldown('search', 30)
                
                if time.time() - last_run < cooldown:
                    await asyncio.sleep(1)
                    continue
                
                if self.global_lock.locked():
                    await self.wait_for_lock("search")
                
                await self.acquire_lock("search")
                
                print(f"\n🔍 [SEARCH] Running search...")
                success = await self.send_command("search")
                
                if success:
                    self.command_last_run['search'] = time.time()
                    response = await self.monitor_for_response(6)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            await self.release_lock()
                            break
                        
                        if 'components' in response:
                            available_locations, location_scores = self.search_solver.analyze_message(response)
                            
                            if not available_locations:
                                print(f"⚠️ [SEARCH] No locations found")
                                await self.release_lock()
                                await asyncio.sleep(5)
                                continue
                            
                            best_location = self.search_solver.choose_best_location(available_locations, location_scores)
                            print(f"📍 Available: {', '.join(available_locations[:3])}...")
                            print(f"🎯 Choosing: {best_location}")
                            
                            click_success = await self.click_button(response, best_location)
                            
                            if click_success:
                                print(f"✅ [SEARCH] Clicked {best_location}")
                                await asyncio.sleep(3)
                            else:
                                print(f"❌ [SEARCH] Failed to click {best_location}")
                    
                    print(f"✅ [SEARCH] Completed")
                
                await self.release_lock()
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [SEARCH] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(30)
        
        print(f"🛑 [SEARCH] Worker stopped")
    
    async def crime_worker(self):
        """Smart Crime Worker with auto-disable"""
        print("👷 Smart Crime Worker started")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [CRIME] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [CRIME] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get('crime', 0)
                cooldown = self.get_command_cooldown('crime', 40)
                
                if time.time() - last_run < cooldown:
                    await asyncio.sleep(1)
                    continue
                
                if self.global_lock.locked():
                    await self.wait_for_lock("crime")
                
                await self.acquire_lock("crime")
                
                print(f"\n🔫 [CRIME] Running smart crime...")
                success = await self.send_command("crime")
                
                if success:
                    self.command_last_run['crime'] = time.time()
                    response = await self.monitor_for_response(6)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            await self.release_lock()
                            break
                        
                        if 'components' in response:
                            available_crimes, crime_scores = self.crime_solver.analyze_crime_options(response)
                            
                            if available_crimes:
                                best_crime = self.crime_solver.choose_best_crime(available_crimes, crime_scores)
                                print(f"⚖️ Crimes: {', '.join(available_crimes)}")
                                print(f"🏆 SELECTING: {best_crime}")
                                
                                click_success = await self.click_button(response, best_crime)
                                
                                if click_success:
                                    print(f"✅ [CRIME] Attempting {best_crime}")
                                    await asyncio.sleep(3)
                    
                    print(f"✅ [CRIME] Completed")
                
                await self.release_lock()
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [CRIME] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(30)
        
        print(f"🛑 [CRIME] Worker stopped")
    
    async def trivia_worker(self):
        """Trivia Worker with auto-disable"""
        print("👷 Trivia Worker started (FIXED AUTO-RECORDING)")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [TRIVIA] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [TRIVIA] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get('trivia', 0)
                cooldown = self.get_command_cooldown('trivia', 40)
                
                if time.time() - last_run < cooldown:
                    await asyncio.sleep(1)
                    continue
                
                if self.global_lock.locked():
                    await self.wait_for_lock("trivia")
                
                await self.acquire_lock("trivia")
                
                print(f"\n❓ [TRIVIA] Running trivia...")
                success = await self.send_command("trivia")
                
                if success:
                    self.command_last_run['trivia'] = time.time()
                    response = await self.monitor_for_response(8)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            await self.release_lock()
                            break
                        
                        if 'embeds' in response:
                            first_embed = response['embeds'][0]
                            description = first_embed.get('description', first_embed.get('rawDescription', ''))
                            
                            lines = description.split('\n')
                            question = lines[0].strip() if lines else ""
                            question = re.sub(r'\*\*', '', question)
                            
                            print(f"📝 Question: {question[:80]}...")
                            
                            answer = self.trivia_solver.find_answer(question)
                            
                            clicked_answer = ""
                            clicked_button = None
                            
                            if answer:
                                print(f"✅ Database answer: {answer}")
                                if 'components' in response:
                                    clicked = False
                                    for row in response['components']:
                                        for btn in row.get('components', []):
                                            btn_label = btn.get('label', '')
                                            if answer.lower() in btn_label.lower() or btn_label.lower() in answer.lower():
                                                await self.click_button(response, btn_label)
                                                clicked_button = btn
                                                clicked_answer = btn_label
                                                print(f"✅ Clicked: {btn_label}")
                                                clicked = True
                                                break
                                        if clicked:
                                            break
                                    
                                    if not clicked and response['components'][0]['components']:
                                        btn = response['components'][0]['components'][0]
                                        await self.click_button(response, btn.get('label'))
                                        clicked_button = btn
                                        clicked_answer = btn.get('label')
                                        print(f"⚠️ Couldn't match, clicked: {btn.get('label')}")
                            else:
                                print(f"⚠️ No answer in database")
                                if 'components' in response and response['components'][0]['components']:
                                    btn = response['components'][0]['components'][0]
                                    await self.click_button(response, btn.get('label'))
                                    clicked_button = btn
                                    clicked_answer = btn.get('label')
                                    print(f"🤔 Guessed: {btn.get('label')}")
                            
                            await asyncio.sleep(2)
                            
                            messages = await self.get_messages(limit=10)
                            updated_msg = None
                            for msg in messages:
                                if msg.get('id') == response['id']:
                                    updated_msg = msg
                                    break
                            
                            if updated_msg and 'embeds' in updated_msg and len(updated_msg['embeds']) > 1:
                                result_embed = updated_msg['embeds'][1]
                                result_desc = result_embed.get('description', '').lower()
                                
                                print(f"📊 Trivia result received")
                                
                                if "no " in result_desc and "the correct answer was" in result_desc:
                                    print(f"❌ WRONG!")
                                    correct_answer = self.trivia_solver.extract_correct_answer_from_response(result_desc)
                                    
                                    if correct_answer:
                                        print(f"📝 Correct answer was: {correct_answer}")
                                        self.trivia_solver.save_answer(question, correct_answer)
                                    else:
                                        print(f"⚠️ Couldn't extract correct answer from response")
                                        print(f"   Response: {result_desc[:100]}...")
                                        
                                elif "you got that answer correct" in result_desc:
                                    print(f"🎉 CORRECT!")
                                    if clicked_answer:
                                        self.trivia_solver.save_answer(question, clicked_answer)
                                    else:
                                        print(f"⚠️ Couldn't save: No clicked answer recorded")
                                else:
                                    print(f"🤔 Unknown result format")
                                    print(f"   Response: {result_desc[:100]}...")
                            else:
                                print(f"⚠️ No result embed found after clicking")
                
                await self.release_lock()
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [TRIVIA] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(30)
        
        print(f"🛑 [TRIVIA] Worker stopped")
    
    async def tidy_worker(self):
        """Tidy Worker with auto-disable"""
        print("👷 Tidy Worker started (NEW BUTTON SYSTEM)")
        
        cooldown = self.get_command_cooldown('tidy', 30)
        print(f"⏰ [TIDY] Using cooldown: {cooldown} seconds")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [TIDY] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [TIDY] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get('tidy', 0)
                
                time_since_last = time.time() - last_run
                if time_since_last < cooldown:
                    remaining = cooldown - time_since_last
                    if remaining > 5:
                        print(f"⏳ [TIDY] Cooldown: {int(remaining)}s remaining")
                    await asyncio.sleep(1)
                    continue
                
                if self.global_lock.locked():
                    await self.wait_for_lock("tidy")
                
                await self.acquire_lock("tidy")
                
                print(f"\n🧹 [TIDY] Starting tidy...")
                success = await self.send_command("tidy")
                
                if success:
                    self.command_last_run['tidy'] = time.time()
                    response = await self.monitor_for_response(6)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            await self.release_lock()
                            break
                        
                        if not response:
                            print("⚠️ [TIDY] No response received")
                            await self.release_lock()
                            await asyncio.sleep(5)
                            continue
                        
                        available_tools = {}
                        
                        hand_custom_id = self.extract_button(response, "hand")
                        if hand_custom_id:
                            available_tools["hand"] = hand_custom_id
                        
                        broom_custom_id = self.extract_button(response, "broom")
                        if broom_custom_id:
                            available_tools["broom"] = broom_custom_id
                        
                        vacuum_custom_id = self.extract_button(response, "vacuum")
                        if vacuum_custom_id:
                            available_tools["vacuum"] = vacuum_custom_id
                        
                        if not available_tools:
                            print("⚠️ [TIDY] No cleaning tools found")
                            await self.release_lock()
                            await asyncio.sleep(5)
                            continue
                        
                        chosen_tool = self.tidy_solver.choose_best_tool_pattern(available_tools)
                        
                        if not chosen_tool:
                            print("❌ [TIDY] Failed to choose tool")
                            await self.release_lock()
                            continue
                        
                        print(f"🎯 Available tools: {list(available_tools.keys())}")
                        print(f"✨ Choosing: {chosen_tool}")
                        
                        click_success = await self.click_button_new(
                            response['id'], 
                            available_tools[chosen_tool]
                        )
                        
                        if click_success:
                            print(f"✅ [TIDY] Clicked {chosen_tool}")
                            
                            await asyncio.sleep(3)
                            result = await self.monitor_for_response(5)
                            
                            if result and 'embeds' in result:
                                embed = result['embeds'][0]
                                description = embed.get('description', '')
                                
                                coins_match = re.search(r'⏣\s*([0-9,]+)', description)
                                if coins_match:
                                    coins = int(coins_match.group(1).replace(',', ''))
                                    print(f"💰 [TIDY] Earned ⏣{coins:,}")
                                    self.tidy_solver.update_stats(chosen_tool, True, coins)
                                else:
                                    print(f"✅ [TIDY] Completed")
                                    self.tidy_solver.update_stats(chosen_tool, True)
                        else:
                            print(f"❌ [TIDY] Failed to click {chosen_tool}")
                            self.tidy_solver.update_stats(chosen_tool, False)
                
                await self.release_lock()
                
                next_run = time.time() + cooldown
                next_time = time.strftime('%H:%M:%S', time.localtime(next_run))
                print(f"⏰ [TIDY] Next run at: {next_time}")
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [TIDY] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(30)
        
        print(f"🛑 [TIDY] Worker stopped")
    
    async def postmemes_worker(self):
        """Postmemes Worker with auto-disable"""
        print("👷 Postmemes Worker started (RANDOM SELECTION)")
        
        base_cooldown = self.get_command_cooldown('postmemes', 25)
        print(f"⏰ [POSTMEMES] Base cooldown: {base_cooldown} seconds")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [POSTMEMES] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [POSTMEMES] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get('postmemes', 0)
                
                if time.time() - last_run < base_cooldown:
                    await asyncio.sleep(1)
                    continue
                
                if self.global_lock.locked():
                    await self.wait_for_lock("postmemes")
                
                await self.acquire_lock("postmemes")
                
                print(f"\n📱 [POSTMEMES] Starting postmemes...")
                success = await self.send_command("postmemes")
                
                if success:
                    self.command_last_run['postmemes'] = time.time()
                    response = await self.monitor_for_response(8)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            await self.release_lock()
                            break
                        
                        if 'components' in response:
                            dropdowns, custom_ids = self.postmemes_solver.extract_dropdown_options(response)
                            
                            if not dropdowns or not custom_ids:
                                print("⚠️ [POSTMEMES] No dropdowns found")
                                await self.release_lock()
                                await asyncio.sleep(5)
                                continue
                            
                            print(f"📊 [POSTMEMES] Found {len(dropdowns)} dropdowns")
                            
                            selections = self.postmemes_solver.choose_random_selections(dropdowns)
                            
                            if not selections or 'platform' not in selections or 'meme_type' not in selections:
                                print("❌ [POSTMEMES] Failed to choose selections")
                                await self.release_lock()
                                continue
                            
                            print(f"🎲 [POSTMEMES] Randomly selected: {selections['platform']} platform, {selections['meme_type']} meme")
                            
                            platform_success = await self.select_dropdown(
                                response['id'],
                                custom_ids['platform'],
                                [selections['platform']]
                            )
                            
                            if not platform_success:
                                print("❌ [POSTMEMES] Failed to select platform")
                                await self.release_lock()
                                await asyncio.sleep(5)
                                continue
                            
                            print(f"✅ [POSTMEMES] Selected platform: {selections['platform']}")
                            await asyncio.sleep(1)
                            
                            meme_type_success = await self.select_dropdown(
                                response['id'],
                                custom_ids['meme_type'],
                                [selections['meme_type']]
                            )
                            
                            if not meme_type_success:
                                print("❌ [POSTMEMES] Failed to select meme type")
                                await self.release_lock()
                                await asyncio.sleep(5)
                                continue
                            
                            print(f"✅ [POSTMEMES] Selected meme type: {selections['meme_type']}")
                            
                            await asyncio.sleep(1)
                            
                            post_button_id = None
                            for row in response.get('components', []):
                                for component in row.get('components', []):
                                    if component.get('type') == 2 and component.get('label') == 'Post':
                                        post_button_id = component.get('custom_id')
                                        break
                                if post_button_id:
                                    break
                            
                            if post_button_id:
                                click_success = await self.click_button_new(response['id'], post_button_id)
                                
                                if click_success:
                                    print(f"✅ [POSTMEMES] Posted meme!")
                                    
                                    await asyncio.sleep(3)
                                    result = await self.monitor_for_response(5)
                                    
                                    coins_earned = 0
                                    is_dead_meme = False
                                    
                                    if result and 'embeds' in result:
                                        embed = result['embeds'][0]
                                        description = embed.get('description', '').lower()
                                        
                                        if "dead meme" in description or "cannot post another meme for another 2 minutes" in description:
                                            is_dead_meme = True
                                            print(f"💀 [POSTMEMES] DEAD MEME DETECTED!")
                                            print(f"   Result: {description[:100]}...")
                                            
                                            base_cooldown = 125
                                            print(f"⏰ [POSTMEMES] Cooldown increased to {base_cooldown}s for dead meme")
                                            
                                        else:
                                            coins_match = re.search(r'⏣\s*([0-9,]+)', description)
                                            if coins_match:
                                                coins_earned = int(coins_match.group(1).replace(',', ''))
                                                print(f"💰 [POSTMEMES] Earned ⏣{coins_earned:,}")
                                            
                                            base_cooldown = self.get_command_cooldown('postmemes', 25)
                                        
                                        print(f"📝 [POSTMEMES] Result: {description[:100]}...")
                                    
                                    if not is_dead_meme:
                                        self.postmemes_solver.update_stats(
                                            selections['platform'],
                                            selections['meme_type'],
                                            True,
                                            coins_earned
                                        )
                                    else:
                                        print(f"📊 [POSTMEMES] Dead meme - not counting in stats")
                                        
                                else:
                                    print(f"❌ [POSTMEMES] Failed to click Post button")
                                    self.postmemes_solver.update_stats(
                                        selections['platform'],
                                        selections['meme_type'],
                                        False
                                    )
                            else:
                                print("⚠️ [POSTMEMES] Post button not found")
                    
                    print(f"✅ [POSTMEMES] Completed")
                
                await self.release_lock()
                
                next_run = time.time() + base_cooldown
                next_time = time.strftime('%H:%M:%S', time.localtime(next_run))
                print(f"⏰ [POSTMEMES] Next run at: {next_time}")
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [POSTMEMES] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(30)
        
        print(f"🛑 [POSTMEMES] Worker stopped")
    
    async def work_worker(self):
        """Work Worker with auto-disable"""
        print("👷 Work Worker started")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [WORK] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [WORK] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get('work', 0)
                cooldown = self.get_command_cooldown('work', 3600)
                
                if time.time() - last_run < cooldown:
                    wait = cooldown - (time.time() - last_run)
                    if wait > 300:
                        await asyncio.sleep(300)
                        continue
                    else:
                        await asyncio.sleep(wait)
                
                if self.global_lock.locked():
                    await self.wait_for_lock("work")
                
                await self.acquire_lock("work")
                
                print(f"\n💼 [WORK] Starting work shift...")
                success = await self.send_command("work", subcommand="shift")
                
                if success:
                    self.command_last_run['work'] = time.time()
                    response = await self.monitor_for_response(8)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            await self.release_lock()
                            break
                    
                    print(f"✅ [WORK] Started shift")
                    
                    for game_num in range(1, 4):
                        print(f"   🎮 Minigame {game_num}/3...")
                        response = await self.monitor_for_response(10)
                        
                        if response:
                            solved = await self.work_solver.solve_minigame(self, response)
                            if solved:
                                print(f"   ✅ Solved")
                        
                        await asyncio.sleep(2)
                    
                    print(f"✅ [WORK] Completed")
                
                await self.release_lock()
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [WORK] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(30)
        
        print(f"🛑 [WORK] Worker stopped")
    
    async def auto_use_worker(self):
        """Simple Auto Use Worker - Just uses items on loop"""
        print("👷 Auto Use Worker started (SIMPLE - NO CHECKS)")
        
        # Check if auto-use is enabled
        if not self.auto_use.is_enabled():
            print("⏭️ [AUTO-USE] Auto-use is disabled in config")
            return
        
        print(f"📦 [AUTO-USE] Monitoring {len(self.auto_use.item_timers)} items")
        
        # Show initial schedule
        print(f"\n📅 [AUTO-USE] Initial schedule:")
        for item_name in self.auto_use.item_timers.keys():
            delay = self.auto_use.item_timers[item_name]['delay']
            quantity = self.auto_use.item_timers[item_name]['quantity']
            
            if delay >= 3600:
                delay_str = f"{delay//3600}h"
            elif delay >= 60:
                delay_str = f"{delay//60}m"
            else:
                delay_str = f"{delay}s"
            
            print(f"   • {item_name.title()}: {quantity}x every {delay_str}")
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [AUTO-USE] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [AUTO-USE] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                # Check if there are items to use
                items_to_use = self.auto_use.get_items_to_use()
                
                if not items_to_use:
                    # No items to use right now, sleep and check again later
                    await asyncio.sleep(60)
                    continue
                
                print(f"\n📦 [AUTO-USE] Found {len(items_to_use)} item(s) to use")
                
                # Process each item that needs to be used
                for item in items_to_use:
                    item_name = item['name']
                    quantity = item['quantity']
                    delay = item['delay']
                    
                    # Format delay for display
                    if delay >= 3600:
                        delay_str = f"{delay//3600}h"
                    elif delay >= 60:
                        delay_str = f"{delay//60}m"
                    else:
                        delay_str = f"{delay}s"
                    
                    print(f"   📦 [{item_name.upper()}] Using {quantity}x (every {delay_str})")
                    
                    # Acquire lock for this operation
                    if self.global_lock.locked():
                        await self.wait_for_lock(f"auto_use_{item_name}")
                    
                    await self.acquire_lock(f"auto_use_{item_name}")
                    
                    try:
                        # Send the use command (no checking, just use)
                        success = await self.send_command("use", item=item_name, quantity=quantity)
                        
                        if success:
                            print(f"   ✅ [{item_name.upper()}] Use command sent")
                            
                            # Wait a bit for the command to process
                            await asyncio.sleep(2)
                            
                            # Check for verification in response (but don't analyze item response)
                            response = await self.monitor_for_response(5)
                            if response:
                                if await self.check_and_handle_verification(response):
                                    print(f"   Stopping all workers...")
                                    await self.release_lock()
                                    break
                            
                            # Update timer
                            self.auto_use.update_timer(item_name)
                            
                        else:
                            print(f"   ❌ [{item_name.upper()}] Failed to send use command")
                        
                    except Exception as e:
                        print(f"   ❌ [{item_name.upper()}] Error during use: {e}")
                    
                    finally:
                        await self.release_lock()
                    
                    # Small delay between using different items
                    await asyncio.sleep(2)
                
                # Show next schedule
                print(f"\n📅 [AUTO-USE] Next schedule:")
                for item_name in self.auto_use.item_timers.keys():
                    next_time = self.auto_use.get_next_use_time(item_name)
                    print(f"   • {item_name.title()}: {next_time}")
                
                # Wait before checking again
                wait_time = 60  # Check every minute
                print(f"\n⏳ [AUTO-USE] Next check in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [AUTO-USE] Error: {e}")
                if self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(60)
        
        print(f"🛑 [AUTO-USE] Worker stopped")
    
    async def fast_command_worker(self, cmd_name: str, needs_lock: bool = False):
        """Fast Command Worker with auto-disable"""
        print(f"👷 {cmd_name.upper()} Worker started")
        
        cooldown = self.get_command_cooldown(cmd_name, 40)
        
        while True:
            try:
                # Check if account is disabled
                if not self.get_account_state():
                    print(f"⛔ [{cmd_name.upper()}] Account disabled in config, stopping...")
                    break
                
                # Check if verification was detected
                if self.verification_required:
                    print(f"⛔ [{cmd_name.upper()}] Stopped - Verification required")
                    await asyncio.sleep(60)
                    continue
                
                last_run = self.command_last_run.get(cmd_name, 0)
                
                if time.time() - last_run < cooldown:
                    await asyncio.sleep(1)
                    continue
                
                if needs_lock and self.global_lock.locked():
                    await self.wait_for_lock(cmd_name)
                
                if needs_lock:
                    await self.acquire_lock(cmd_name)
                
                print(f"\n⚡ [{cmd_name.upper()}] Running...")
                success = await self.send_command(cmd_name)
                
                if success:
                    self.command_last_run[cmd_name] = time.time()
                    response = await self.monitor_for_response(6)
                    
                    if response:
                        # Check for verification and disable account
                        if await self.check_and_handle_verification(response):
                            print(f"   Stopping all workers...")
                            if needs_lock:
                                await self.release_lock()
                            break
                    
                    if needs_lock:
                        if response and 'components' in response:
                            buttons = response['components'][0]['components']
                            if buttons:
                                await self.click_button(response, buttons[0].get('label'))
                    
                    print(f"✅ [{cmd_name.upper()}] Completed")
                
                if needs_lock:
                    await self.release_lock()
                
                random_delay = random.uniform(1, 3)
                await asyncio.sleep(random_delay)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ [{cmd_name.upper()}] Error: {e}")
                if needs_lock and self.global_lock.locked():
                    await self.release_lock()
                await asyncio.sleep(10)
        
        print(f"🛑 [{cmd_name.upper()}] Worker stopped")
    
    async def run_smart_system(self):
        print("\n" + "="*50)
        print(f"🤖 ULTIMATE DANK MEMER BOT - Account {self.account_index}")
        print(f"🚨 AUTO-DISABLE ON VERIFICATION ENABLED")
        print(f"📦 SIMPLE AUTO-USE SYSTEM (NO CHECKS)")
        print("="*50)
        print(f"📅 Started at: {time.strftime('%H:%M:%S')}")
        print(f"📁 Config: {self.config_path}")
        print("="*50)
        
        enabled_commands = []
        print("📊 Enabled commands with delays:")
        for cmd_name, cmd_config in self.config.get('commands', {}).items():
            if cmd_config.get('state', True):
                enabled_commands.append(cmd_name)
                delay = cmd_config.get('delay', cmd_config.get('cooldown', self.get_command_cooldown(cmd_name, 40)))
                print(f"   • {cmd_name.upper()}: {delay}s cooldown")
        
        print("\n🧠 SMART FEATURES:")
        print("  • 🚨 Auto-disable on verification detection")
        print("  • 🔍 Smart Search - Selects best locations")
        print("  • 🔫 Smart Crime - Selects HIGHEST scoring crime")
        print("  • ❓ Trivia - FIXED AUTO-RECORDING")
        print("  • 🧹 Tidy - NEW button system")
        print("  • 📱 Postmemes - RANDOM selection")
        print("  • 📦 Auto-Use - SIMPLE (just uses items on loop)")
        print("="*50)
        
        tasks = []
        
        if 'search' in enabled_commands:
            tasks.append(asyncio.create_task(self.search_worker()))
            print("✅ Smart Search Worker started")
        
        if 'crime' in enabled_commands:
            tasks.append(asyncio.create_task(self.crime_worker()))
            print("✅ Smart Crime Worker started")
        
        if 'trivia' in enabled_commands:
            tasks.append(asyncio.create_task(self.trivia_worker()))
            print("✅ Trivia Worker started")
            trivia_stats = self.trivia_solver.get_stats()
            print(f"   📚 Database has {trivia_stats['total_questions']} questions")

        if 'tidy' in enabled_commands:
            tasks.append(asyncio.create_task(self.tidy_worker()))
            print("✅ Tidy Worker started")
        
        if 'postmemes' in enabled_commands:
            tasks.append(asyncio.create_task(self.postmemes_worker()))
            print("✅ Postmemes Worker started")
        
        if 'work' in enabled_commands:
            tasks.append(asyncio.create_task(self.work_worker()))
            print("✅ Work Worker started")
        
        # Add auto-use worker if enabled
        if self.auto_use.is_enabled():
            tasks.append(asyncio.create_task(self.auto_use_worker()))
            print("✅ Auto Use Worker started (SIMPLE)")
            
            # Show auto-use items
            auto_use_items = self.config.get('autoUse', {}).get('items', {})
            enabled_items = [name for name, config in auto_use_items.items() 
                           if config.get('state', False)]
            if enabled_items:
                print(f"   📦 Auto-using: {', '.join(enabled_items)}")
        
        fast_commands = {
            'beg': False,
            'dig': False,
            'hunt': False,
            'highlow': True,
            'stream': False,
        }
        
        for cmd_name, needs_lock in fast_commands.items():
            if cmd_name in enabled_commands:
                tasks.append(asyncio.create_task(
                    self.fast_command_worker(cmd_name, needs_lock=needs_lock)
                ))
                print(f"✅ {cmd_name.upper()} Worker started")
        
        print(f"\n🎯 Total workers: {len(tasks)}")
        print("="*50)
        print("🚀 ALL SYSTEMS GO! Bot is running...")
        print("="*50)
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all workers...")
            for task in tasks:
                task.cancel()
            await asyncio.sleep(1)
        
        # Show final stats for this account
        print(f"\n📊 FINAL STATS FOR ACCOUNT {self.account_index}:")
        trivia_stats = self.trivia_solver.get_stats()
        print(f"   ❓ Trivia: {trivia_stats['total_questions']} questions in database")
        print(f"      Added {trivia_stats['new_answers_added']} new answers this session")
        
        if hasattr(self, 'postmemes_solver'):
            pm_stats = self.postmemes_solver.stats
            if pm_stats['attempts'] > 0:
                success_rate = (pm_stats['successes'] / pm_stats['attempts']) * 100
                print(f"   📱 Postmemes: {pm_stats['attempts']} attempts, {pm_stats['successes']} successes ({success_rate:.1f}%)")
                if pm_stats['earnings'] > 0:
                    print(f"      Earned ⏣{pm_stats['earnings']:,}")
        
        # Show auto-use stats
        if hasattr(self, 'auto_use') and self.auto_use.is_enabled():
            auto_use_stats = self.auto_use.get_stats()
            if auto_use_stats['total_items'] > 0:
                print(f"   📦 Auto-Use: {auto_use_stats['total_uses']} uses total")
                for item_name, stats in auto_use_stats['items'].items():
                    if stats['uses'] > 0:
                        print(f"      • {item_name.title()}: {stats['uses']} uses")
        
        if self.verification_required:
            print(f"   🚨 VERIFICATION DETECTED - Account disabled")
        else:
            print(f"   ✅ Account still enabled")
        
        print(f"👋 Account {self.account_index} stopped")

# ============================================================================
# MAIN FUNCTION WITH MULTI-ACCOUNT SUPPORT
# ============================================================================
async def main():
    print("""
╔═══════════════════════════════════════════════════════╗
║      ULTIMATE DANK MEMER BOT                         ║
║      • 🚨 AUTO-DISABLE on Verification               ║
║      • 🔄 Multi-account support                      ║
║      • 📁 Creates logs/ directory                    ║
║      • ⏰ Auto-stops disabled accounts               ║
║      • 📦 SIMPLE Auto-Use (just uses on loop)       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    # DEBUG: Show current directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config.json: {e}")
        return
    
    if not config.get('accounts'):
        print("❌ No accounts in config")
        return
    
    # Filter to only enabled accounts
    enabled_accounts = []
    for i, acc in enumerate(config['accounts']):
        if acc.get('state', True):
            enabled_accounts.append((i, acc))
    
    if not enabled_accounts:
        print("❌ No enabled accounts in config")
        return
    
    print(f"📊 Found {len(enabled_accounts)} enabled account(s)")
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Run bots for each enabled account
    tasks = []
    for acc_index, acc in enabled_accounts:
        print(f"\n➡️  Starting bot for account {acc_index}:")
        print(f"   Channel: {acc['channelID']}")
        print(f"   Token: {acc['token'][:20]}...")
        
        bot = SmartDankBot(
            token=acc['token'],
            channel_id=acc['channelID'],
            guild_id=acc.get('guildID'),
            account_index=acc_index,
            config_path='config.json'
        )
        
        # Create task for each bot
        async def run_single_bot(bot_instance):
            async with bot_instance:
                await bot_instance.run_smart_system()
        
        tasks.append(asyncio.create_task(run_single_bot(bot)))
        
        # Small delay between starting accounts
        await asyncio.sleep(2)
    
    # Wait for all bots to complete
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all bots...")
        for task in tasks:
            task.cancel()
        
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*50)
    print("📊 SESSION SUMMARY:")
    
    # Load final config to show disabled accounts
    try:
        with open('config.json', 'r') as f:
            final_config = json.load(f)
        
        disabled_count = sum(1 for acc in final_config.get('accounts', []) 
                           if not acc.get('state', True))
        enabled_count = sum(1 for acc in final_config.get('accounts', []) 
                          if acc.get('state', True))
        
        print(f"   ✅ Enabled accounts: {enabled_count}")
        print(f"   🚫 Disabled accounts: {disabled_count}")
        
        if disabled_count > 0:
            print(f"\n   📋 DISABLED ACCOUNTS:")
            for i, acc in enumerate(final_config.get('accounts', [])):
                if not acc.get('state', True):
                    print(f"      Account {i}: {acc['token'][:20]}... (Channel: {acc['channelID']})")
        
        # Check if verification log exists
        if os.path.exists('logs/verification_log.json'):
            print(f"\n   📝 Verification log: logs/verification_log.json")
                
    except Exception as e:
        print(f"   ❌ Could not load final config: {e}")
    
    print("="*50)
    print("👋 All bots stopped")
    print("="*50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()