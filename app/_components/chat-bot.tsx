'use client'

import { useState } from 'react';
import { Textarea } from "./catalyst/textarea";
import { Button } from './catalyst/button';
import { Dialog, DialogTitle, DialogDescription, DialogBody, DialogActions } from './catalyst/dialog';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

interface ChatBotProps {
  setResults: (results: any[]) => void;
}

export const ChatBot = ({ setResults }: ChatBotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hi, how can I help you today?", sender: 'bot' }
  ]);
  const [input, setInput] = useState<string>('');
  const [order, setOrder] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    const userMessage: Message = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    const response = await fetch(`/api/chat?message=${input}`);
    const data = await response.json();
    console.log(data)
    const botMessage: Message = { text: data.response, sender: 'bot' };
    setMessages((prev) => [...prev, botMessage]);
    if (data.order) {
      setOrder(data.order);
      setIsModalOpen(true);
    }
    setResults(data.results);  // Pass results to parent
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(e);
    }
  };

  const ChatBubble = ({ msg, index }: { msg: Message, index: number }) => (
    <div
      key={index}
      className={`p-2 rounded-lg px-4 ${msg.sender === 'user' ? 'bg-blue-100' : 'bg-slate-100'}`}
    >
      {msg.text}
    </div>
  );

  return (
    <div className='w-full rounded-lg border border-slate-200 p-4'>
      <div className='space-y-2 mb-8 flex flex-col'>
        {messages.map((msg, index) => <ChatBubble key={index} msg={msg} index={index} />)}
      </div>
      <form onSubmit={sendMessage} className='space-y-2 flex flex-col items-end'>
        <Textarea
          className="h-16"
          resizable={false}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <Button type="submit" className="cursor-pointer">
          Send
        </Button>
      </form>
      <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <DialogTitle>Order Details</DialogTitle>
        <DialogDescription>Please confirm the order details below:</DialogDescription>
        <DialogBody>{order}</DialogBody>
        <DialogActions>
          <Button onClick={() => setIsModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

