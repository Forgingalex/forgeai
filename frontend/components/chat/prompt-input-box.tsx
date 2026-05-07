'use client'

import * as DialogPrimitive from '@radix-ui/react-dialog'
import * as TooltipPrimitive from '@radix-ui/react-tooltip'
import { AnimatePresence, motion } from 'framer-motion'
import {
  ArrowUp,
  BrainCog,
  FolderCog,
  Globe,
  Mic,
  Paperclip,
  Square,
  StopCircle,
  X,
} from 'lucide-react'
import React from 'react'

import { cn } from '@/lib/utils'

export type PromptMode = 'chat' | 'search' | 'think' | 'canvas'

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  className?: string
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({ className, ...props }, ref) => (
  <textarea
    className={cn(
      'flex min-h-[44px] w-full resize-none rounded-md border-none bg-transparent px-3 py-2.5 text-base text-gray-100 placeholder:text-gray-400 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50',
      className
    )}
    ref={ref}
    rows={1}
    {...props}
  />
))
Textarea.displayName = 'Textarea'

const TooltipProvider = TooltipPrimitive.Provider
const Tooltip = TooltipPrimitive.Root
const TooltipTrigger = TooltipPrimitive.Trigger

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 6, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      'z-50 overflow-hidden rounded-md border border-white/10 bg-[#0a0a0b]/95 px-3 py-1.5 text-sm text-white shadow-xl backdrop-blur-md',
      className
    )}
    {...props}
  />
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

const Dialog = DialogPrimitive.Root
const DialogPortal = DialogPrimitive.Portal

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn('fixed inset-0 z-50 bg-black/70 backdrop-blur-sm', className)}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed left-1/2 top-1/2 z-50 grid w-full max-w-[90vw] -translate-x-1/2 -translate-y-1/2 gap-4 rounded-2xl border border-white/10 bg-[#0a0a0b] p-0 shadow-2xl md:max-w-[800px]',
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 z-10 rounded-full bg-white/10 p-2 transition hover:bg-white/15">
        <X className="h-5 w-5 text-gray-200" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogTitle = DialogPrimitive.Title

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'ghost'
  size?: 'default' | 'icon'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    const variantClasses = {
      default: 'bg-[#ecad29] text-black hover:bg-[#d99d25]',
      ghost: 'bg-transparent text-gray-300 hover:bg-white/10 hover:text-white',
    }
    const sizeClasses = {
      default: 'h-10 px-4 py-2',
      icon: 'h-8 w-8 rounded-full',
    }

    return (
      <button
        className={cn(
          'inline-flex items-center justify-center font-medium transition focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50',
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

interface PromptInputContextType {
  disabled?: boolean
  isLoading: boolean
  maxHeight: number | string
  onSubmit?: () => void
  setValue: (value: string) => void
  value: string
}

const PromptInputContext = React.createContext<PromptInputContextType>({
  disabled: false,
  isLoading: false,
  maxHeight: 240,
  setValue: () => undefined,
  value: '',
})

function usePromptInput() {
  return React.useContext(PromptInputContext)
}

interface PromptInputProps {
  children: React.ReactNode
  className?: string
  disabled?: boolean
  isLoading?: boolean
  maxHeight?: number | string
  onDragLeave?: (event: React.DragEvent) => void
  onDragOver?: (event: React.DragEvent) => void
  onDrop?: (event: React.DragEvent) => void
  onSubmit?: () => void
  onValueChange?: (value: string) => void
  value?: string
}

const PromptInput = React.forwardRef<HTMLDivElement, PromptInputProps>(
  (
    {
      children,
      className,
      disabled = false,
      isLoading = false,
      maxHeight = 240,
      onDragLeave,
      onDragOver,
      onDrop,
      onSubmit,
      onValueChange,
      value,
    },
    ref
  ) => {
    const [internalValue, setInternalValue] = React.useState(value || '')
    const handleChange = (newValue: string) => {
      setInternalValue(newValue)
      onValueChange?.(newValue)
    }

    return (
      <TooltipProvider>
        <PromptInputContext.Provider
          value={{
            disabled,
            isLoading,
            maxHeight,
            onSubmit,
            setValue: onValueChange ?? handleChange,
            value: value ?? internalValue,
          }}
        >
          <div
            ref={ref}
            className={cn(
              'rounded-3xl border border-white/10 bg-[#0a0a0b]/70 p-2 shadow-[0_18px_60px_rgba(0,0,0,0.38)] backdrop-blur-2xl transition',
              isLoading && 'border-[#ecad29]/50',
              className
            )}
            onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            onDrop={onDrop}
          >
            {children}
          </div>
        </PromptInputContext.Provider>
      </TooltipProvider>
    )
  }
)
PromptInput.displayName = 'PromptInput'

function PromptInputTextarea({
  className,
  disableAutosize = false,
  onKeyDown,
  placeholder,
  ...props
}: React.ComponentProps<typeof Textarea> & { disableAutosize?: boolean }) {
  const { disabled, maxHeight, onSubmit, setValue, value } = usePromptInput()
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  React.useEffect(() => {
    if (disableAutosize || !textareaRef.current) return
    textareaRef.current.style.height = 'auto'
    textareaRef.current.style.height =
      typeof maxHeight === 'number'
        ? `${Math.min(textareaRef.current.scrollHeight, maxHeight)}px`
        : `min(${textareaRef.current.scrollHeight}px, ${maxHeight})`
  }, [disableAutosize, maxHeight, value])

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      onSubmit?.()
    }
    onKeyDown?.(event)
  }

  return (
    <Textarea
      ref={textareaRef}
      value={value}
      onChange={(event) => setValue(event.target.value)}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      placeholder={placeholder}
      className={cn('text-base', className)}
      {...props}
    />
  )
}

function PromptInputActions({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('flex items-center gap-2', className)} {...props}>
      {children}
    </div>
  )
}

function PromptInputAction({
  children,
  tooltip,
  side = 'top',
}: {
  children: React.ReactNode
  side?: 'top' | 'bottom' | 'left' | 'right'
  tooltip: React.ReactNode
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent side={side}>{tooltip}</TooltipContent>
    </Tooltip>
  )
}

function CustomDivider() {
  return (
    <div className="relative mx-1 h-6 w-px">
      <div className="absolute inset-0 rounded-full bg-gradient-to-t from-transparent via-[#ecad29]/60 to-transparent" />
    </div>
  )
}

function VoiceRecorder({
  isRecording,
  onStopRecording,
}: {
  isRecording: boolean
  onStopRecording: (duration: number) => void
}) {
  const [time, setTime] = React.useState(0)

  React.useEffect(() => {
    if (!isRecording) return undefined
    const timer = window.setInterval(() => setTime((current) => current + 1), 1000)
    return () => window.clearInterval(timer)
  }, [isRecording])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  if (!isRecording) return null

  return (
    <div className="flex w-full flex-col items-center justify-center py-3">
      <div className="mb-3 flex items-center gap-2">
        <div className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
        <span className="font-mono text-sm text-white/80">{formatTime(time)}</span>
      </div>
      <div className="flex h-10 w-full items-center justify-center gap-0.5 px-4">
        {Array.from({ length: 32 }).map((_, index) => (
          <div
            key={index}
            className="w-0.5 animate-pulse rounded-full bg-white/50"
            style={{
              animationDelay: `${index * 0.04}s`,
              height: `${28 + ((index * 17) % 70)}%`,
            }}
          />
        ))}
      </div>
      <button className="sr-only" onClick={() => onStopRecording(time)}>
        Stop recording
      </button>
    </div>
  )
}

function ImageViewDialog({ imageUrl, onClose }: { imageUrl: string | null; onClose: () => void }) {
  if (!imageUrl) return null
  return (
    <Dialog open={Boolean(imageUrl)} onOpenChange={onClose}>
      <DialogContent className="border-none bg-transparent shadow-none">
        <DialogTitle className="sr-only">Image preview</DialogTitle>
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          className="overflow-hidden rounded-2xl bg-[#0a0a0b] shadow-2xl"
        >
          <img src={imageUrl} alt="Full preview" className="max-h-[80vh] w-full rounded-2xl object-contain" />
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}

interface PromptInputBoxProps {
  className?: string
  isLoading?: boolean
  onModeChange?: (mode: PromptMode) => void
  onSend?: (message: string, files: File[], mode: PromptMode) => void
  placeholder?: string
}

export const PromptInputBox = React.forwardRef<HTMLDivElement, PromptInputBoxProps>(
  ({ className, isLoading = false, onModeChange, onSend = () => undefined, placeholder = 'Ask ForgeAI...' }, ref) => {
    const [input, setInput] = React.useState('')
    const [files, setFiles] = React.useState<File[]>([])
    const [filePreviews, setFilePreviews] = React.useState<Record<string, string>>({})
    const [isRecording, setIsRecording] = React.useState(false)
    const [mode, setMode] = React.useState<PromptMode>('chat')
    const [selectedImage, setSelectedImage] = React.useState<string | null>(null)
    const uploadInputRef = React.useRef<HTMLInputElement>(null)

    const selectMode = (nextMode: PromptMode) => {
      const resolvedMode = mode === nextMode ? 'chat' : nextMode
      setMode(resolvedMode)
      onModeChange?.(resolvedMode)
    }

    const processFile = React.useCallback((file: File) => {
      if (!file.type.startsWith('image/') || file.size > 10 * 1024 * 1024) return
      setFiles([file])
      const reader = new FileReader()
      reader.onload = (event) => setFilePreviews({ [file.name]: String(event.target?.result || '') })
      reader.readAsDataURL(file)
    }, [])

    const handleDrop = React.useCallback(
      (event: React.DragEvent) => {
        event.preventDefault()
        const imageFile = Array.from(event.dataTransfer.files).find((file) => file.type.startsWith('image/'))
        if (imageFile) processFile(imageFile)
      },
      [processFile]
    )

    React.useEffect(() => {
      const handlePaste = (event: ClipboardEvent) => {
        const item = Array.from(event.clipboardData?.items || []).find((entry) => entry.type.startsWith('image/'))
        const file = item?.getAsFile()
        if (file) {
          event.preventDefault()
          processFile(file)
        }
      }
      document.addEventListener('paste', handlePaste)
      return () => document.removeEventListener('paste', handlePaste)
    }, [processFile])

    const handleSubmit = () => {
      if (!input.trim() && files.length === 0) return
      onSend(input.trim(), files, mode)
      setInput('')
      setFiles([])
      setFilePreviews({})
    }

    const hasContent = input.trim() !== '' || files.length > 0

    const modeButton = (
      currentMode: PromptMode,
      label: string,
      Icon: React.ComponentType<{ className?: string }>,
      activeClass: string
    ) => (
      <button
        type="button"
        onClick={() => selectMode(currentMode)}
        className={cn(
          'flex h-8 items-center gap-1 rounded-full border border-transparent px-2 py-1 text-[#9CA3AF] transition hover:text-[#D1D5DB]',
          mode === currentMode && activeClass
        )}
      >
        <motion.div
          animate={{ rotate: mode === currentMode ? 360 : 0, scale: mode === currentMode ? 1.08 : 1 }}
          transition={{ type: 'spring', stiffness: 260, damping: 24 }}
        >
          <Icon className="h-4 w-4" />
        </motion.div>
        <AnimatePresence>
          {mode === currentMode && (
            <motion.span
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 'auto', opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              className="overflow-hidden whitespace-nowrap text-xs"
            >
              {label}
            </motion.span>
          )}
        </AnimatePresence>
      </button>
    )

    return (
      <>
        <PromptInput
          value={input}
          onValueChange={setInput}
          isLoading={isLoading}
          onSubmit={handleSubmit}
          disabled={isLoading || isRecording}
          ref={ref}
          className={className}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={(event) => event.preventDefault()}
          onDrop={handleDrop}
        >
          {files.length > 0 && !isRecording && (
            <div className="flex flex-wrap gap-2 pb-1">
              {files.map((file, index) => (
                <div key={file.name} className="group relative">
                  {filePreviews[file.name] && (
                    <button
                      type="button"
                      className="h-16 w-16 overflow-hidden rounded-xl"
                      onClick={() => setSelectedImage(filePreviews[file.name])}
                    >
                      <img src={filePreviews[file.name]} alt={file.name} className="h-full w-full object-cover" />
                    </button>
                  )}
                  <button
                    type="button"
                    className="absolute right-1 top-1 rounded-full bg-black/70 p-0.5"
                    onClick={() => {
                      setFiles(files.filter((_, itemIndex) => itemIndex !== index))
                      setFilePreviews({})
                    }}
                  >
                    <X className="h-3 w-3 text-white" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {!isRecording && (
            <PromptInputTextarea
              placeholder={
                mode === 'search'
                  ? 'Search the selected knowledge workspace...'
                  : mode === 'think'
                    ? 'Think deeply with Gemini Pro...'
                    : mode === 'canvas'
                      ? 'Create in chat and canvas...'
                      : placeholder
              }
            />
          )}

          <VoiceRecorder
            isRecording={isRecording}
            onStopRecording={(duration) => {
              setIsRecording(false)
              onSend(`[Voice message - ${duration} seconds]`, [], mode)
            }}
          />

          <PromptInputActions className="justify-between pt-2">
            <div className={cn('flex items-center gap-1', isRecording && 'invisible h-0 opacity-0')}>
              <PromptInputAction tooltip="Upload image">
                <button
                  type="button"
                  className="flex h-8 w-8 items-center justify-center rounded-full text-[#9CA3AF] transition hover:bg-white/10 hover:text-[#D1D5DB]"
                  onClick={() => uploadInputRef.current?.click()}
                >
                  <Paperclip className="h-5 w-5" />
                  <input
                    ref={uploadInputRef}
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={(event) => {
                      const file = event.target.files?.[0]
                      if (file) processFile(file)
                      event.currentTarget.value = ''
                    }}
                  />
                </button>
              </PromptInputAction>
              {modeButton('search', 'Search', Globe, 'border-[#ecad29]/80 bg-[#ecad29]/10 text-[#ecad29]')}
              <CustomDivider />
              {modeButton('think', 'Think', BrainCog, 'border-[#facc15]/80 bg-[#facc15]/10 text-[#facc15]')}
              <CustomDivider />
              {modeButton('canvas', 'Canvas', FolderCog, 'border-[#d97706]/80 bg-[#d97706]/10 text-[#d97706]')}
            </div>

            <PromptInputAction tooltip={isLoading ? 'Generating' : isRecording ? 'Stop recording' : hasContent ? 'Send' : 'Voice'}>
              <Button
                variant={hasContent ? 'default' : 'ghost'}
                size="icon"
                className="rounded-full"
                onClick={() => {
                  if (isRecording) setIsRecording(false)
                  else if (hasContent) handleSubmit()
                  else setIsRecording(true)
                }}
                disabled={isLoading && !hasContent}
              >
                {isLoading ? (
                  <Square className="h-4 w-4 fill-current" />
                ) : isRecording ? (
                  <StopCircle className="h-5 w-5 text-red-400" />
                ) : hasContent ? (
                  <ArrowUp className="h-4 w-4" />
                ) : (
                  <Mic className="h-5 w-5" />
                )}
              </Button>
            </PromptInputAction>
          </PromptInputActions>
        </PromptInput>

        <ImageViewDialog imageUrl={selectedImage} onClose={() => setSelectedImage(null)} />
      </>
    )
  }
)
PromptInputBox.displayName = 'PromptInputBox'
