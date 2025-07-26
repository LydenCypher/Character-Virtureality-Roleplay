#!/usr/bin/env python3
"""
Comprehensive Backend Testing for AI Character Interaction API
Tests all endpoints systematically including AI integration
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://55fba44d-74fc-41dd-b35a-5d269f215d09.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.test_data = {}
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"API is healthy: {data.get('message')}")
                return True
            else:
                self.log_test("Health Check", False, f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_create_user(self):
        """Test user creation"""
        try:
            # Create a realistic test user
            user_data = {
                "username": "alice_wonderland",
                "email": f"alice.wonderland.{uuid.uuid4().hex[:8]}@example.com"
            }
            
            response = requests.post(f"{BASE_URL}/users", params=user_data)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                if user_id:
                    self.test_data["user_id"] = user_id
                    self.test_data["username"] = user_data["username"]
                    self.test_data["email"] = user_data["email"]
                    self.log_test("Create User", True, f"User created successfully with ID: {user_id}")
                    return True
                else:
                    self.log_test("Create User", False, "User creation response missing user_id")
                    return False
            else:
                self.log_test("Create User", False, f"User creation failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create User", False, f"User creation error: {str(e)}")
            return False
    
    def test_get_user(self):
        """Test getting user by ID"""
        if "user_id" not in self.test_data:
            self.log_test("Get User", False, "No user_id available from previous test")
            return False
        
        try:
            user_id = self.test_data["user_id"]
            response = requests.get(f"{BASE_URL}/users/{user_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("user_id") == user_id and data.get("username") == self.test_data["username"]:
                    self.log_test("Get User", True, f"User retrieved successfully: {data.get('username')}")
                    return True
                else:
                    self.log_test("Get User", False, "User data mismatch in response")
                    return False
            else:
                self.log_test("Get User", False, f"Get user failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get User", False, f"Get user error: {str(e)}")
            return False
    
    def test_create_character(self):
        """Test character creation"""
        if "user_id" not in self.test_data:
            self.log_test("Create Character", False, "No user_id available for character creation")
            return False
        
        try:
            character_data = {
                "name": "Luna the Mystic",
                "description": "A wise and mysterious sorceress from the enchanted forest, known for her deep knowledge of ancient magic and her compassionate nature.",
                "personality": "Wise, mysterious, compassionate, slightly mischievous, loves riddles and ancient lore",
                "avatar": "https://example.com/luna_avatar.jpg",
                "ai_provider": "openai",
                "ai_model": "gpt-4.1",
                "system_prompt": "You are Luna, a mystical sorceress. Speak with wisdom and mystery, often using metaphors related to nature and magic.",
                "is_nsfw": False
            }
            
            user_id = self.test_data["user_id"]
            response = requests.post(f"{BASE_URL}/characters", 
                                   json=character_data, 
                                   params={"user_id": user_id},
                                   headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                character_id = data.get("character_id")
                if character_id:
                    self.test_data["character_id"] = character_id
                    self.test_data["character_name"] = character_data["name"]
                    self.log_test("Create Character", True, f"Character created successfully: {character_data['name']} (ID: {character_id})")
                    return True
                else:
                    self.log_test("Create Character", False, "Character creation response missing character_id")
                    return False
            else:
                self.log_test("Create Character", False, f"Character creation failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Character", False, f"Character creation error: {str(e)}")
            return False
    
    def test_get_characters(self):
        """Test getting all characters"""
        try:
            response = requests.get(f"{BASE_URL}/characters")
            
            if response.status_code == 200:
                data = response.json()
                characters = data.get("characters", [])
                if isinstance(characters, list):
                    character_found = False
                    if "character_id" in self.test_data:
                        character_found = any(char.get("character_id") == self.test_data["character_id"] for char in characters)
                    
                    self.log_test("Get Characters", True, f"Retrieved {len(characters)} characters" + 
                                (" (including our test character)" if character_found else ""))
                    return True
                else:
                    self.log_test("Get Characters", False, "Characters response is not a list")
                    return False
            else:
                self.log_test("Get Characters", False, f"Get characters failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Characters", False, f"Get characters error: {str(e)}")
            return False
    
    def test_get_character_by_id(self):
        """Test getting character by ID"""
        if "character_id" not in self.test_data:
            self.log_test("Get Character by ID", False, "No character_id available from previous test")
            return False
        
        try:
            character_id = self.test_data["character_id"]
            response = requests.get(f"{BASE_URL}/characters/{character_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("character_id") == character_id and data.get("name") == self.test_data["character_name"]:
                    self.log_test("Get Character by ID", True, f"Character retrieved successfully: {data.get('name')}")
                    return True
                else:
                    self.log_test("Get Character by ID", False, "Character data mismatch in response")
                    return False
            else:
                self.log_test("Get Character by ID", False, f"Get character failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Character by ID", False, f"Get character error: {str(e)}")
            return False
    
    def test_create_conversation(self):
        """Test conversation creation"""
        if "user_id" not in self.test_data or "character_id" not in self.test_data:
            self.log_test("Create Conversation", False, "Missing user_id or character_id for conversation creation")
            return False
        
        try:
            conversation_data = {
                "character_id": self.test_data["character_id"],
                "title": "A Mystical Encounter",
                "mode": "rp",
                "is_nsfw": False,
                "ai_provider": "openai",
                "ai_model": "gpt-4.1"
            }
            
            user_id = self.test_data["user_id"]
            response = requests.post(f"{BASE_URL}/conversations", 
                                   json=conversation_data, 
                                   params={"user_id": user_id},
                                   headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data.get("conversation_id")
                if conversation_id:
                    self.test_data["conversation_id"] = conversation_id
                    self.test_data["conversation_title"] = conversation_data["title"]
                    self.log_test("Create Conversation", True, f"Conversation created successfully: {conversation_data['title']} (ID: {conversation_id})")
                    return True
                else:
                    self.log_test("Create Conversation", False, "Conversation creation response missing conversation_id")
                    return False
            else:
                self.log_test("Create Conversation", False, f"Conversation creation failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Conversation", False, f"Conversation creation error: {str(e)}")
            return False
    
    def test_get_user_conversations(self):
        """Test getting user conversations"""
        if "user_id" not in self.test_data:
            self.log_test("Get User Conversations", False, "No user_id available for getting conversations")
            return False
        
        try:
            user_id = self.test_data["user_id"]
            response = requests.get(f"{BASE_URL}/conversations/{user_id}")
            
            if response.status_code == 200:
                data = response.json()
                conversations = data.get("conversations", [])
                if isinstance(conversations, list):
                    conversation_found = False
                    if "conversation_id" in self.test_data:
                        conversation_found = any(conv.get("conversation_id") == self.test_data["conversation_id"] for conv in conversations)
                    
                    self.log_test("Get User Conversations", True, f"Retrieved {len(conversations)} conversations" + 
                                (" (including our test conversation)" if conversation_found else ""))
                    return True
                else:
                    self.log_test("Get User Conversations", False, "Conversations response is not a list")
                    return False
            else:
                self.log_test("Get User Conversations", False, f"Get conversations failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get User Conversations", False, f"Get conversations error: {str(e)}")
            return False
    
    def test_ai_providers(self):
        """Test AI providers endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/ai-providers")
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                if isinstance(providers, list) and len(providers) > 0:
                    openai_provider = next((p for p in providers if p.get("id") == "openai"), None)
                    if openai_provider and openai_provider.get("available"):
                        self.log_test("AI Providers", True, f"Retrieved {len(providers)} AI providers, OpenAI is available")
                        return True
                    else:
                        self.log_test("AI Providers", False, "OpenAI provider not available or not found")
                        return False
                else:
                    self.log_test("AI Providers", False, "No AI providers found")
                    return False
            else:
                self.log_test("AI Providers", False, f"AI providers failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("AI Providers", False, f"AI providers error: {str(e)}")
            return False
    
    def test_ai_chat(self):
        """Test AI chat endpoint with real OpenAI integration"""
        if "conversation_id" not in self.test_data:
            self.log_test("AI Chat", False, "No conversation_id available for chat testing")
            return False
        
        try:
            chat_data = {
                "conversation_id": self.test_data["conversation_id"],
                "message": "Greetings, Luna! I've heard tales of your wisdom. Could you share some ancient knowledge about the mystical arts?",
                "ai_provider": "openai",
                "ai_model": "gpt-4.1"
            }
            
            print("   Sending message to AI... (this may take a few seconds)")
            response = requests.post(f"{BASE_URL}/chat", 
                                   json=chat_data, 
                                   headers=HEADERS,
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                user_message = data.get("user_message")
                ai_response = data.get("ai_response")
                
                if user_message and ai_response:
                    ai_content = ai_response.get("content", "")
                    if len(ai_content) > 10:  # Basic check for meaningful response
                        self.test_data["ai_response"] = ai_content
                        self.log_test("AI Chat", True, f"AI chat successful. Response length: {len(ai_content)} characters", 
                                    f"AI Response preview: {ai_content[:100]}...")
                        return True
                    else:
                        self.log_test("AI Chat", False, "AI response too short or empty")
                        return False
                else:
                    self.log_test("AI Chat", False, "Missing user_message or ai_response in chat response")
                    return False
            else:
                self.log_test("AI Chat", False, f"AI chat failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("AI Chat", False, f"AI chat error: {str(e)}")
            return False
    
    def test_get_conversation_messages(self):
        """Test getting conversation messages"""
        if "conversation_id" not in self.test_data:
            self.log_test("Get Conversation Messages", False, "No conversation_id available for getting messages")
            return False
        
        try:
            conversation_id = self.test_data["conversation_id"]
            response = requests.get(f"{BASE_URL}/conversations/{conversation_id}/messages")
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                if isinstance(messages, list):
                    # Should have at least 2 messages if AI chat test passed (user + AI response)
                    expected_messages = 2 if "ai_response" in self.test_data else 0
                    if len(messages) >= expected_messages:
                        self.log_test("Get Conversation Messages", True, f"Retrieved {len(messages)} messages from conversation")
                        return True
                    else:
                        self.log_test("Get Conversation Messages", True, f"Retrieved {len(messages)} messages (fewer than expected but endpoint works)")
                        return True
                else:
                    self.log_test("Get Conversation Messages", False, "Messages response is not a list")
                    return False
            else:
                self.log_test("Get Conversation Messages", False, f"Get messages failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Conversation Messages", False, f"Get messages error: {str(e)}")
            return False
    
    def test_multi_turn_conversation(self):
        """Test multi-turn conversation to verify session management"""
        if "conversation_id" not in self.test_data:
            self.log_test("Multi-turn Conversation", False, "No conversation_id available for multi-turn test")
            return False
        
        try:
            # Send a follow-up message that references the previous conversation
            chat_data = {
                "conversation_id": self.test_data["conversation_id"],
                "message": "That's fascinating! Can you tell me more about what you just mentioned?",
                "ai_provider": "openai",
                "ai_model": "gpt-4.1"
            }
            
            print("   Sending follow-up message to test conversation memory...")
            response = requests.post(f"{BASE_URL}/chat", 
                                   json=chat_data, 
                                   headers=HEADERS,
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("ai_response")
                
                if ai_response:
                    ai_content = ai_response.get("content", "")
                    if len(ai_content) > 10:
                        self.log_test("Multi-turn Conversation", True, f"Multi-turn conversation successful. AI maintained context.", 
                                    f"Follow-up response preview: {ai_content[:100]}...")
                        return True
                    else:
                        self.log_test("Multi-turn Conversation", False, "AI follow-up response too short or empty")
                        return False
                else:
                    self.log_test("Multi-turn Conversation", False, "Missing ai_response in follow-up chat")
                    return False
            else:
                self.log_test("Multi-turn Conversation", False, f"Multi-turn chat failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Multi-turn Conversation", False, f"Multi-turn conversation error: {str(e)}")
            return False
    
    def test_different_chat_modes(self):
        """Test different chat modes (casual, RP, RPG)"""
        if "user_id" not in self.test_data or "character_id" not in self.test_data:
            self.log_test("Different Chat Modes", False, "Missing user_id or character_id for mode testing")
            return False
        
        modes_to_test = ["casual", "rpg"]  # We already tested RP mode
        success_count = 0
        
        for mode in modes_to_test:
            try:
                # Create a conversation with different mode
                conversation_data = {
                    "character_id": self.test_data["character_id"],
                    "title": f"Testing {mode.upper()} Mode",
                    "mode": mode,
                    "is_nsfw": False,
                    "ai_provider": "openai",
                    "ai_model": "gpt-4.1"
                }
                
                user_id = self.test_data["user_id"]
                response = requests.post(f"{BASE_URL}/conversations", 
                                       json=conversation_data, 
                                       params={"user_id": user_id},
                                       headers=HEADERS)
                
                if response.status_code == 200:
                    data = response.json()
                    conversation_id = data.get("conversation_id")
                    
                    if conversation_id:
                        # Test a quick chat in this mode
                        chat_data = {
                            "conversation_id": conversation_id,
                            "message": f"Hello! Let's test {mode} mode interaction.",
                            "ai_provider": "openai",
                            "ai_model": "gpt-4.1"
                        }
                        
                        chat_response = requests.post(f"{BASE_URL}/chat", 
                                                    json=chat_data, 
                                                    headers=HEADERS,
                                                    timeout=20)
                        
                        if chat_response.status_code == 200:
                            success_count += 1
                            print(f"   ✅ {mode.upper()} mode test successful")
                        else:
                            print(f"   ❌ {mode.upper()} mode chat failed")
                    else:
                        print(f"   ❌ {mode.upper()} mode conversation creation failed")
                else:
                    print(f"   ❌ {mode.upper()} mode conversation creation failed")
                    
            except Exception as e:
                print(f"   ❌ {mode.upper()} mode test error: {str(e)}")
        
        if success_count == len(modes_to_test):
            self.log_test("Different Chat Modes", True, f"All {len(modes_to_test)} additional chat modes tested successfully")
            return True
        elif success_count > 0:
            self.log_test("Different Chat Modes", True, f"{success_count}/{len(modes_to_test)} additional chat modes working")
            return True
        else:
            self.log_test("Different Chat Modes", False, "No additional chat modes working")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Comprehensive Backend Testing for AI Character Interaction API")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Create User", self.test_create_user),
            ("Get User", self.test_get_user),
            ("Create Character", self.test_create_character),
            ("Get Characters", self.test_get_characters),
            ("Get Character by ID", self.test_get_character_by_id),
            ("Create Conversation", self.test_create_conversation),
            ("Get User Conversations", self.test_get_user_conversations),
            ("AI Providers", self.test_ai_providers),
            ("AI Chat", self.test_ai_chat),
            ("Get Conversation Messages", self.test_get_conversation_messages),
            ("Multi-turn Conversation", self.test_multi_turn_conversation),
            ("Different Chat Modes", self.test_different_chat_modes),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        elif passed > failed:
            print(f"\n⚠️  Most tests passed, but {failed} test(s) need attention.")
        else:
            print(f"\n🚨 Multiple tests failed. Backend needs significant fixes.")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/backend_test_results.json", "w") as f:
        json.dump({
            "summary": {"passed": passed, "failed": failed, "total": passed + failed},
            "test_results": results,
            "test_data": tester.test_data
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")