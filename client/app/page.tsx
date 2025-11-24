"use client";

import * as React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { GraphView } from "@/components/GraphView";

export default function HomePage() {
  const API_BASE = "http://localhost:8000";

  const [dialogOpen, setDialogOpen] = useState<boolean>(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isGraphUpdating, setIsGraphUpdating] = useState<boolean>(false);
  const [updateGraphVisual, setUpdateGraphVisual] = useState<boolean>(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState<string>("");
  const [focusedNode, setFocusedNode] = useState<string | null>(null);

  const handleUpdateGraph = async () => {
    setIsGraphUpdating(true);
    try {
      const response = await fetch(`${API_BASE}/process`, {
        method: "POST",
      });

      if (!response.ok) {
        const error = await response.text();
        console.error(error);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsGraphUpdating(false);
      setUpdateGraphVisual((prev) => !prev);
    }
  };

  const handleUpload = async (file: File | null) => {
    if (!file) return;

    setUploadError(null);
    setSelectedFile(file);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const name = file.name.toLowerCase();
      let endpoint = "";
      if (
        name.endsWith(".png") ||
        name.endsWith(".jpg") ||
        name.endsWith(".jpeg")
      ) {
        endpoint = "/add/image";
      } else if (name.endsWith(".mp3")) {
        endpoint = "/add/audio";
      } else if (name.endsWith(".pdf") || name.endsWith(".txt")) {
        endpoint = "/add/text";
      } else {
        setUploadError("Unsupported file type");
        return;
      }

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.text();
        console.error(error);
        setUploadError("Failed to upload file");
        return;
      }

      handleUpdateGraph();
      setDialogOpen(false);
    } catch (error) {
      console.error(error);
      setUploadError("Failed to upload file");
    } finally {
      setSelectedFile(null);
    }
  };

  const handleChat = async (message: string) => {
    try {
      setMessages((prev) => [...prev, message]);

      const formData = new FormData();
      formData.append("message", message);

      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.text();
        console.error(error);
        return;
      }

      const data = await response.json();
      console.log(data);
      setMessages((prev) => [...prev, data.content]);
      setFocusedNode(data.node["name"]);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      {/* Main column */}
      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-emerald-400 to-sky-500" />
            <div className="flex flex-col leading-tight">
              <span className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Multimodal RAG
              </span>
              <span className="text-base font-medium text-slate-50">
                Starter Pokemons: Generation 1
              </span>
            </div>
          </div>

          <Button onClick={() => setDialogOpen(true)}>Upload</Button>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogContent className="border-slate-800 bg-slate-950 text-slate-100 sm:max-w-md">
              <DialogHeader>
                <DialogTitle className="text-sm font-medium">
                  Upload document or media
                </DialogTitle>
                <DialogDescription
                  className={`text-xs ${uploadError ? "text-red-500" : "text-slate-400"}`}
                >
                  {uploadError ?? "Pick a PDF, text, image, or audio file"}
                </DialogDescription>
              </DialogHeader>

              <div className="mt-3 space-y-3">
                <label className="block text-xs font-medium text-slate-300">
                  File
                </label>
                <label
                  className={cn(
                    "flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/80 px-4 py-8 text-center text-xs text-slate-400 hover:border-emerald-500/70 hover:bg-slate-900",
                  )}
                >
                  <input
                    type="file"
                    className="hidden"
                    onChange={(e) => {
                      const f = e.target.files?.[0] ?? null;
                      handleUpload(f);
                    }}
                  />
                  <div className="mb-1 text-[11px] font-medium uppercase tracking-[0.16em] text-slate-500">
                    Click to choose a file
                  </div>
                  <div className="text-[11px] text-slate-500">
                    PDF, TXT, PNG, JPG, MP3
                  </div>
                  {selectedFile && (
                    <div className="mt-3 text-[11px] text-emerald-300">
                      Selected: {selectedFile.name}
                    </div>
                  )}
                </label>
              </div>

              <div className="mt-4 flex justify-end gap-2">
                <DialogClose asChild>
                  <Button
                    variant="ghost"
                    className="text-xs text-slate-400 hover:bg-slate-900 hover:text-slate-100"
                    onClick={() => {
                      setSelectedFile(null);
                      setDialogOpen(false);
                    }}
                  >
                    Cancel
                  </Button>
                </DialogClose>
              </div>
            </DialogContent>
          </Dialog>
        </header>

        {/* Content split */}
        <main className="flex flex-1 overflow-hidden">
          {/* Chat column */}
          <section className="flex w-[420px] max-w-md flex-col border-r border-slate-800 bg-slate-950/70">
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto px-4 py-4">
              <div className="flex flex-col gap-2">
                {messages.map((msg, idx) => {
                  const isUser = idx % 2 === 0; // assuming user message, then bot reply alternates
                  return (
                    <div
                      key={idx}
                      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={cn(
                          "max-w-[75%] px-4 py-2 rounded-2xl break-words",
                          isUser
                            ? "bg-emerald-500 text-slate-950 rounded-br-none"
                            : "bg-slate-800 text-slate-100 rounded-bl-none",
                        )}
                      >
                        <p className="text-sm">{msg}</p>
                        <span
                          className={`block mt-1 text-[10px] text-right ${isUser ? " text-black" : " text-slate-400"}`}
                        >
                          {new Date().toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </div>
                  );
                })}
                <div
                  ref={(el) => el && el.scrollIntoView({ behavior: "smooth" })}
                />
              </div>
            </div>

            {/* Input */}
            <div className="border-t border-slate-800 bg-slate-950/90 px-4 py-3">
              <form
                className="flex items-end gap-2"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleChat(input);
                  setInput("");
                }}
              >
                <Textarea
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="min-h-[44px] max-h-[120px] flex-1 resize-none rounded-2xl border-slate-700 bg-slate-900/80 text-sm text-slate-100 placeholder:text-slate-500 focus-visible:ring-emerald-500/60"
                  placeholder="Ask about Bulbasaur, Charmander, or Squirtle..."
                />
                <Button
                  type="submit"
                  size="icon"
                  disabled={!input}
                  className="h-9 w-9 rounded-full bg-emerald-500 text-slate-950 hover:bg-emerald-400 disabled:opacity-40"
                >
                  <span className="sr-only">Send</span>
                  <svg
                    viewBox="0 0 24 24"
                    className="h-4 w-4"
                    aria-hidden="true"
                  >
                    <path
                      d="M5 12L4.2 3.6C4.14 2.98 4.8 2.57 5.34 2.88L20 11L5.34 19.12C4.8 19.43 4.14 19.02 4.2 18.4L5 10H13"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={1.6}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </Button>
              </form>
            </div>
          </section>

          {/* Graph area */}
          <section className="relative flex flex-1 bg-slate-900/80">
            <div className="flex h-full w-full flex-col px-6 py-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-medium text-slate-200">
                  Knowledge graph
                </h2>
                <span className="rounded-full border border-slate-700 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-slate-500">
                  {isGraphUpdating ? "Syncing..." : "Synced"}
                </span>
              </div>

              <GraphView updateGraphVisual={updateGraphVisual} />
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
