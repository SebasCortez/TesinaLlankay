"""
Módulo de servicios e integraciones externas para Llankay
"""
from .groq_agent import obtener_cliente_groq, generar_respuesta_agente

__all__ = ['obtener_cliente_groq', 'generar_respuesta_agente']
