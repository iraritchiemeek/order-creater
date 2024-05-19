'use client'

import { useState } from 'react';
import Image from "next/image";
import Link from "next/link";
import { ChatBot } from "./_components/chat-bot";
import { Result, Results } from "./_components/results";

export default function Home() {
  const [results, setResults] = useState<Result[]>([]);

  return (
    <main className="mx-auto max-w-8xl px-4 py-4 sm:px-6 lg:px-8 h-screen flex flex-col gap-4">
      <h2 id="category-heading" className="text-2xl font-bold tracking-tight text-gray-900">
        Te Papa archives AI search
      </h2>
      <div className="w-1/2">
        <ChatBot setResults={setResults} />
      </div>
      <div >
        <Results results={results} />
      </div>
    </main>
  );
}
