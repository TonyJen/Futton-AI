import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAgents, getRecommendations, runAgent, approveRecommendation, rejectRecommendation, chatWithSupervisor } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { AgentCard } from '@/components/manufacturing/AgentCard';
import { RecommendationCard } from '@/components/manufacturing/RecommendationCard';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { Bot, Send } from 'lucide-react';
import { toast } from 'sonner';
import type { Agent, AgentRecommendation } from '@/lib/types';

export default function Agents() {
  const queryClient = useQueryClient();
  const [runningAgent, setRunningAgent] = useState<number | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'agent'; text: string }>>([
    { role: 'agent', text: 'Hello! I\'m the Funton AI Supervisor. I\'m powered by an LLM on the backend. Ask me about inventory, production, demand, or what the agents should focus on.' }
  ]);
  const [processingRec, setProcessingRec] = useState<number | null>(null);

  const { data: agents = [] } = useQuery({ queryKey: ['agents'], queryFn: getAgents });
  const { data: recommendations = [] } = useQuery({ 
    queryKey: ['all-recommendations'], 
    queryFn: () => getRecommendations() 
  });

  const pending = recommendations.filter(r => r.status === 'PENDING');
  const executed = recommendations.filter(r => r.status !== 'PENDING');

  const runAgentMutation = useMutation({
    mutationFn: runAgent,
    onMutate: (id) => setRunningAgent(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['all-recommendations'] });
      toast.success(`Agent completed — ${data.recommendations.length} new recommendations generated`);
    },
    onSettled: () => setRunningAgent(null),
  });

  const approveMutation = useMutation({
    mutationFn: approveRecommendation,
    onMutate: (id) => setProcessingRec(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-recommendations'] });
      toast.success('Action executed successfully');
    },
    onSettled: () => setProcessingRec(null),
  });

  const rejectMutation = useMutation({
    mutationFn: rejectRecommendation,
    onMutate: (id) => setProcessingRec(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-recommendations'] });
      toast.info('Recommendation rejected');
    },
    onSettled: () => setProcessingRec(null),
  });

  const handleRunAgent = (id: number) => runAgentMutation.mutate(id);

  // Real AI Supervisor powered by backend LLM (with full conversation context)
  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput.trim();

    setChatHistory(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatInput('');

    try {
      const historyForBackend = chatHistory.map(m => ({
        role: m.role === 'agent' ? 'agent' : 'user',
        text: m.text,
      }));
      historyForBackend.push({ role: 'user', text: userMsg });

      const result = await chatWithSupervisor(historyForBackend);

      setChatHistory(prev => [...prev, { role: 'agent', text: result.response }]);

      if (result.suggested_agent) {
        setTimeout(() => {
          setChatHistory(prev => [
            ...prev,
            { role: 'agent', text: `Would you like me to run the ${result.suggested_agent} agent?` }
          ]);
        }, 400);
      }
    } catch (err) {
      setChatHistory(prev => [
        ...prev,
        { role: 'agent', text: "I couldn't connect to the AI Supervisor right now. Is the backend running?" }
      ]);
    }
  };

  return (
    <div>
      <Header 
        title="AI Agents Hub" 
        subtitle="LangGraph agents with full human-in-the-loop approval" 
      />

      {/* Chat / Supervisor */}
      <Card className="mb-8 border-primary-100 bg-gradient-to-r from-white to-primary-50/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-primary-700">
            <Bot className="h-5 w-5" /> Ask the AI Supervisor
            <Badge variant="neutral" className="text-[10px] ml-1">LLM</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-white rounded-xl p-4 h-44 overflow-y-auto mb-3 border text-sm space-y-3 data-scroll">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={msg.role === 'user' ? 'text-right' : ''}>
                <div className={`inline-block max-w-[82%] px-4 py-2 rounded-2xl ${msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-slate-100 text-slate-800'}`}>
                  {msg.text}
                </div>
              </div>
            ))}
          </div>
          <form onSubmit={handleChat} className="flex gap-2">
            <Input 
              value={chatInput} 
              onChange={(e) => setChatInput(e.target.value)} 
              placeholder="What should we focus on? Any shortages? Capacity issues?" 
              className="flex-1" 
            />
            <Button type="submit"><Send className="h-4 w-4" /></Button>
          </form>
        </CardContent>
      </Card>

      {/* Agent Cards */}
      <div className="mb-6">
        <h3 className="font-semibold tracking-tight mb-4">Available Agents</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4">
          {agents.map((agent: Agent) => (
            <AgentCard 
              key={agent.id} 
              agent={agent} 
              onRun={handleRunAgent} 
              isRunning={runningAgent === agent.id} 
            />
          ))}
        </div>
      </div>

      {/* Approval Queue */}
      <div className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold tracking-tight">Approval Queue <Badge variant="warning">{pending.length} pending</Badge></h3>
        </div>

        {pending.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {pending.map((rec: AgentRecommendation) => (
              <RecommendationCard
                key={rec.id}
                rec={rec}
                onApprove={(id) => approveMutation.mutate(id)}
                onReject={(id) => rejectMutation.mutate(id)}
                isProcessing={processingRec === rec.id}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-10 border rounded-2xl text-slate-500">All agent proposals reviewed.</div>
        )}
      </div>

      {/* Executed / History */}
      {executed.length > 0 && (
        <div className="mt-10">
          <h3 className="font-semibold tracking-tight mb-3 text-sm text-slate-500">RECENTLY EXECUTED OR REJECTED</h3>
          <div className="space-y-2">
            {executed.slice(0, 4).map((rec: AgentRecommendation) => (
              <div key={rec.id} className="flex items-center justify-between bg-white border rounded-xl px-5 py-3 text-sm">
                <div>
                  <span className="font-semibold">{rec.title}</span>
                  <span className="text-slate-500 ml-3">— {rec.agentName}</span>
                </div>
                <Badge variant={rec.status === 'APPROVED' ? 'success' : 'danger'}>{rec.status}</Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
