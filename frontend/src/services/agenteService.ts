import api from './api'

export interface MensajeTurno {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  error?: boolean
  uso?: {
    prompt_tokens?: number
    completion_tokens?: number
    total_tokens?: number
  }
}

export interface ChatAgenteRequest {
  mensaje?: string
  historial: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>
  system_prompt?: string
  modelo?: string
  temperatura?: number
  max_tokens?: number
}

export interface ChatAgenteResponse {
  exito: boolean
  respuesta: string | null
  error?: string | null
  tipo_error?: string | null
  uso?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  } | null
  cuota?: {
    restantes: number
    limite_diario: number
    segundos_reinicio: number
  } | null
  modelo: string
}

/**
 * Envía la conversación al agente conversacional con Groq y LLaMA 3.3 70B
 */
export const enviarMensajeChat = async (datos: ChatAgenteRequest): Promise<ChatAgenteResponse> => {
  try {
    const response = await api.post<ChatAgenteResponse>('/agente/chat/', datos)
    return response.data
  } catch (error: any) {
    if (error.response?.data) {
      return error.response.data as ChatAgenteResponse
    }
    return {
      exito: false,
      respuesta: null,
      error: error.message || 'Error de conexión con el servidor',
      tipo_error: 'connection',
      uso: null,
      modelo: 'llama-3.3-70b-versatile',
    }
  }
}
