import Image from "next/image";
import Link from "next/link";
import { ChatBot } from "./_components/chat-bot";

export default function Home() {
  return (
    <main className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 h-screen flex items-center">
      <ChatBot />
    </main>
  );
}
