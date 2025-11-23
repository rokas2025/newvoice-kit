'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { useSessionContext, useSessionMessages } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useConnection } from '@/hooks/useConnection';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(true); // Always show chat transcript
  const { isConnectionActive, startDisconnectTransition } = useConnection();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Performance stats state
  const [stats, setStats] = useState({
    sttDuration: 0,
    llmDuration: 0,
    ttsDuration: 0,
    totalDuration: 0,
  });

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }

    // Parse timing information from agent messages
    messages.forEach((msg) => {
      const text = msg.message;
      if (text.includes('[STATS]')) {
        const sttMatch = text.match(/STT:(\d+)ms/);
        const llmMatch = text.match(/LLM:(\d+)ms/);
        const ttsMatch = text.match(/TTS:(\d+)ms/);
        const totalMatch = text.match(/TOTAL:(\d+)ms/);

        if (sttMatch) setStats((prev) => ({ ...prev, sttDuration: parseInt(sttMatch[1]) }));
        if (llmMatch) setStats((prev) => ({ ...prev, llmDuration: parseInt(llmMatch[1]) }));
        if (ttsMatch) setStats((prev) => ({ ...prev, ttsDuration: parseInt(ttsMatch[1]) }));
        if (totalMatch) setStats((prev) => ({ ...prev, totalDuration: parseInt(totalMatch[1]) }));
      }
    });
  }, [messages]);

  return (
    <section className="bg-background relative z-10 h-full w-full overflow-hidden" {...props}>
      {/* Performance Stats Overlay */}
      {isConnectionActive && (
        <div className="bg-background/90 fixed top-4 right-4 z-50 space-y-2 rounded-lg border p-4 text-sm shadow-lg backdrop-blur-sm">
          <div className="text-xs font-semibold tracking-wide uppercase opacity-70">
            Performance Stats
          </div>
          <div className="space-y-1">
            <div className="flex justify-between gap-4">
              <span className="opacity-70">STT:</span>
              <span className="font-mono font-semibold">{stats.sttDuration}ms</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="opacity-70">LLM:</span>
              <span className="font-mono font-semibold">{stats.llmDuration}ms</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="opacity-70">TTS:</span>
              <span className="font-mono font-semibold">{stats.ttsDuration}ms</span>
            </div>
            <div className="flex justify-between gap-4 border-t pt-2">
              <span className="font-semibold">Total:</span>
              <span className="font-mono font-bold">{stats.totalDuration}ms</span>
            </div>
          </div>
        </div>
      )}

      {/* Chat Transcript */}
      <div
        className={cn(
          'fixed inset-0 grid grid-cols-1 grid-rows-1',
          !chatOpen && 'pointer-events-none'
        )}
      >
        <Fade top className="absolute inset-x-4 top-0 h-40" />
        <ScrollArea ref={scrollAreaRef} className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[200px]">
          <ChatTranscript
            hidden={!chatOpen}
            messages={messages}
            className="mx-auto max-w-2xl space-y-3 transition-opacity duration-300 ease-out"
          />
        </ScrollArea>
      </div>

      {/* Tile Layout */}
      <TileLayout chatOpen={chatOpen} />

      {/* Bottom */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}
        <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar
            controls={controls}
            isConnectionActive={isConnectionActive}
            onDisconnect={startDisconnectTransition}
            onChatOpenChange={setChatOpen}
          />
        </div>
      </MotionBottom>
    </section>
  );
};
