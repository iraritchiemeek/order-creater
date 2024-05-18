'use client'

import { useState } from 'react';
import Image from "next/image";
import Link from "next/link";
import { ChatBot } from "./_components/chat-bot";
import { Results } from "./_components/results";

export default function Home() {
  const [results, setResults] = useState([]);

  return (
    <main className="mx-auto max-w-8xl px-4 py-4 sm:px-6 lg:px-8 h-screen flex flex-col gap-4">
      <div className="w-1/2">
        <ChatBot setResults={setResults} />
      </div>
      <div >
        <Results results={results} />
      </div>
    </main>
  );
}
