export type RolUsuario = 'cliente' | 'trabajador' | 'admin';

export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  rol: RolUsuario;
  celular: string;
  distrito: string;
  foto?: string | null;
  foto_url?: string | null;
  reputacion_promedio?: number | null;
  num_calificaciones?: number;
  fecha_registro: string;
}

export type CategoriaTrabajador =
  | 'Electricidad'
  | 'Gasfitería'
  | 'Carpintería'
  | 'Cerrajería'
  | 'Pintura';

export type EstadoTrabajador = 'pendiente' | 'aprobado' | 'rechazado';

export interface Trabajador {
  id: number;
  usuario: Usuario;
  categoria: CategoriaTrabajador;
  oficio: string;
  experiencia: string;
  descripcion: string;
  disponible: boolean;
  calificacion_promedio: number;
  num_calificaciones: number;
  latitud?: number | null;
  longitud?: number | null;
  distancia_km?: number | null;
  estado: EstadoTrabajador;
  motivo_rechazo?: string;
  fecha_solicitud: string;
  fecha_aprobacion?: string | null;
  foto?: string | null;
  foto_url?: string | null;
}

export type EstadoSolicitud =
  | 'pendiente'
  | 'aceptado'
  | 'en_progreso'
  | 'completado'
  | 'rechazado';

export interface Solicitud {
  id: number;
  cliente: Usuario;
  trabajador: Trabajador;
  mensaje: string;
  descripcion_problema: string;
  direccion: string;
  estado: EstadoSolicitud;
  motivo_rechazo?: string;
  precio_acordado?: number | null;
  metodo_pago?: string;
  ha_calificado_trabajador?: boolean;
  ha_calificado_cliente?: boolean;
  fecha_solicitud: string;
  fecha_actualizacion: string;
}

export interface Calificacion {
  id: number;
  trabajador: number;
  cliente: Usuario;
  solicitud?: number | null;
  puntuacion: number;
  comentario: string;
  fecha: string;
}

export interface CalificacionCliente {
  id: number;
  trabajador: Trabajador;
  cliente: Usuario;
  solicitud?: number | null;
  puntuacion: number;
  comentario: string;
  fecha: string;
}

export interface Notificacion {
  id: number;
  titulo: string;
  mensaje: string;
  tipo: string;
  leida: boolean;
  enlace: string;
  fecha_creacion: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  usuario: Usuario;
}

export interface AdminStats {
  total_clientes: number;
  total_trabajadores: number;
  pendientes_aprobacion: number;
  total_solicitudes: number;
  solicitudes_completadas: number;
  total_calificaciones: number;
}

export type EstadoRequerimiento = 'pendiente' | 'contactado' | 'asignado' | 'atendido' | 'cancelado';

export interface RequerimientoOficio {
  id: number;
  cliente: Usuario;
  nombre_contacto: string;
  celular_contacto: string;
  distrito: string;
  oficio_solicitado: string;
  descripcion: string;
  estado: EstadoRequerimiento;
  notas_admin: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

