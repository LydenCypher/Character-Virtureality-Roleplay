import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { MessageCircle, Plus, Users, Zap, Brain, Globe, Heart } from 'lucide-react';
import axios from 'axios';

const Home = () => {
  const { user } = useAuth();
  const [recentConversations, setRecentConversations] = useState([]);
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [conversationsRes, charactersRes] = await Promise.all([
        axios.get(`${backendUrl}/api/conversations/${user.user_id}`),
        axios.get(`${backendUrl}/api/characters?limit=8`)
      ]);

      setRecentConversations(conversationsRes.data.conversations.slice(0, 5));
      setCharacters(charactersRes.data.characters);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = async (characterId) => {
    try {
      const response = await axios.post(`${backendUrl}/api/conversations`, {
        character_id: characterId,
        title: `New Chat`,
        mode: 'casual',
        is_nsfw: false
      }, {
        params: { user_id: user.user_id }
      });

      if (response.data.conversation_id) {
        window.location.href = `/chat/${response.data.conversation_id}`;
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  const features = [
    {
      icon: Brain,
      title: 'Multi-AI Support',
      description: 'Switch between OpenAI, Anthropic Claude, and Google Gemini',
      color: 'text-blue-600'
    },
    {
      icon: MessageCircle,
      title: 'Multiple Chat Modes',
      description: 'Casual, Roleplay, and RPG-style interactions',
      color: 'text-green-600'
    },
    {
      icon: Users,
      title: 'Character Creation',
      description: 'Create custom AI characters with unique personalities',
      color: 'text-purple-600'
    },
    {
      icon: Globe,
      title: 'Multi-Language',
      description: 'Chat in any language with AI characters',
      color: 'text-orange-600'
    },
    {
      icon: Zap,
      title: 'Real-time Chat',
      description: 'Instant responses with streaming support',
      color: 'text-yellow-600'
    },
    {
      icon: Heart,
      title: 'NSFW Support',
      description: 'Mature content support for adult conversations',
      color: 'text-red-600'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-dark-900 dark:to-dark-800">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-4">
            Welcome to AI Characters
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Interact with AI characters through voice, video, and text. Create your own characters and explore endless possibilities.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/characters"
              className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white px-8 py-3 rounded-lg font-medium hover:from-primary-700 hover:to-secondary-700 transition-all duration-200 transform hover:scale-105"
            >
              Explore Characters
            </Link>
            <Link
              to="/create-character"
              className="bg-white dark:bg-dark-700 text-primary-600 dark:text-primary-400 px-8 py-3 rounded-lg font-medium border-2 border-primary-600 hover:bg-primary-50 dark:hover:bg-dark-600 transition-all duration-200"
            >
              Create Character
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className={`${feature.color} mb-4`}>
                  <Icon className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Recent Conversations */}
        {recentConversations.length > 0 && (
          <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-sm mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Recent Conversations
            </h2>
            <div className="space-y-3">
              {recentConversations.map((conversation) => (
                <Link
                  key={conversation.conversation_id}
                  to={`/chat/${conversation.conversation_id}`}
                  className="block p-4 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-primary-500 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {conversation.title}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(conversation.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 px-2 py-1 rounded">
                        {conversation.mode}
                      </span>
                      <MessageCircle className="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Popular Characters */}
        <div className="bg-white dark:bg-dark-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Popular Characters
            </h2>
            <Link
              to="/characters"
              className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
            >
              View All
            </Link>
          </div>
          
          {characters.length === 0 ? (
            <div className="text-center py-8">
              <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                No characters available yet.
              </p>
              <Link
                to="/create-character"
                className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
              >
                Create the first character
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {characters.map((character) => (
                <div
                  key={character.character_id}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-primary-500 transition-colors cursor-pointer"
                  onClick={() => startNewConversation(character.character_id)}
                >
                  <div className="flex items-center space-x-3 mb-3">
                    {character.avatar ? (
                      <img
                        src={character.avatar}
                        alt={character.name}
                        className="character-avatar"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-medium">
                          {character.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {character.name}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {character.ai_provider} • {character.ai_model}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                    {character.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {character.is_nsfw && (
                        <span className="text-xs bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 px-2 py-1 rounded">
                          NSFW
                        </span>
                      )}
                    </div>
                    <button className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium">
                      Start Chat
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;