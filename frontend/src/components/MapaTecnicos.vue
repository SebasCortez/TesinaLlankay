<template>
    <div class="mapa-wrap">
        <div id="mapa" ref="mapaRef"></div>
        <div class="mapa-leyenda">
            <div class="leyenda-item"><span class="dot azul"></span> Tu ubicación</div>
            <div class="leyenda-item"><span class="dot verde"></span> Disponible</div>
            <div class="leyenda-item"><span class="dot gris"></span> Ocupado</div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps<{
    tecnicos: any[]
    latUsuario?: number | null
    lonUsuario?: number | null
}>()

const emit = defineEmits(['seleccionar'])
const mapaRef = ref<HTMLElement | null>(null)
let mapa: L.Map | null = null
let marcadores: L.Marker[] = []
let circulo: L.Circle | null = null

const CUSCO = [-13.5170, -71.9785]

function getIcono(disponible: boolean) {
    const color = disponible ? '#10B981' : '#9CA3AF'
    return L.divIcon({
        className: '',
        html: `
      <div style="
        width:36px;height:36px;border-radius:50%;
        background:${color};border:3px solid #fff;
        box-shadow:0 2px 8px rgba(0,0,0,0.25);
        display:flex;align-items:center;justify-content:center;
        font-size:14px;font-weight:700;color:#fff;
      ">🔧</div>
    `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -20],
    })
}

function iconoUsuario() {
    return L.divIcon({
        className: '',
        html: `
      <div style="
        width:16px;height:16px;border-radius:50%;
        background:#2563EB;border:3px solid #fff;
        box-shadow:0 0 0 4px rgba(37,99,235,0.25);
      "></div>
    `,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
    })
}

function limpiarMarcadores() {
    marcadores.forEach(m => m.remove())
    marcadores = []
    if (circulo) { circulo.remove(); circulo = null }
}

function agregarMarcadores() {
    limpiarMarcadores()
    if (!mapa) return

    // Marcador usuario
    if (props.latUsuario && props.lonUsuario) {
        const m = L.marker([props.latUsuario, props.lonUsuario], { icon: iconoUsuario() })
            .addTo(mapa)
            .bindPopup('<strong>Tu ubicación</strong>')
        marcadores.push(m)

        circulo = L.circle([props.latUsuario, props.lonUsuario], {
            radius: 5000,
            color: '#2563EB',
            fillColor: '#2563EB',
            fillOpacity: 0.05,
            weight: 1.5,
            dashArray: '6,6',
        }).addTo(mapa)

        mapa.setView([props.latUsuario, props.lonUsuario], 14)
    }

    // Marcadores técnicos
    props.tecnicos.forEach(t => {
        if (!t.latitud || !t.longitud) return
        const m = L.marker([t.latitud, t.longitud], { icon: getIcono(t.disponible) })
            .addTo(mapa!)
            .bindPopup(`
        <div style="min-width:180px;font-family:Inter,sans-serif">
          <div style="font-size:14px;font-weight:700;margin-bottom:4px">
            ${t.usuario.first_name} ${t.usuario.last_name}
          </div>
          <div style="font-size:12px;color:#6B7280;margin-bottom:6px">${t.oficio}</div>
          <div style="font-size:12px;margin-bottom:8px">
            ⭐ ${t.calificacion_promedio.toFixed(1)} · ${t.disponible ? '🟢 Disponible' : '⚫ Ocupado'}
            ${t.distancia_km ? ` · 📍 ${t.distancia_km} km` : ''}
          </div>
          <button onclick="window.verPerfil(${t.id})" style="
            background:#2563EB;color:#fff;border:none;
            padding:6px 14px;border-radius:6px;font-size:12px;
            font-weight:600;cursor:pointer;width:100%
          ">Ver perfil</button>
        </div>
      `)
        marcadores.push(m)
    })

    // Ajustar vista si hay técnicos
    if (props.tecnicos.filter(t => t.latitud && t.longitud).length > 0 && !props.latUsuario) {
        const bounds = L.latLngBounds(
            props.tecnicos
                .filter(t => t.latitud && t.longitud)
                .map(t => [t.latitud, t.longitud] as [number, number])
        )
        mapa.fitBounds(bounds, { padding: [40, 40] })
    }
}

onMounted(() => {
    if (!mapaRef.value) return

    mapa = L.map(mapaRef.value, {
        center: CUSCO as [number, number],
        zoom: 14,
        zoomControl: true,
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 19,
    }).addTo(mapa)

        // Función global para ver perfil desde popup
        ; (window as any).verPerfil = (id: number) => {
            emit('seleccionar', id)
        }

    agregarMarcadores()
})

onUnmounted(() => {
    if (mapa) { mapa.remove(); mapa = null }
    delete (window as any).verPerfil
})

watch(() => [props.tecnicos, props.latUsuario, props.lonUsuario], () => {
    agregarMarcadores()
}, { deep: true })
</script>

<style scoped>
.mapa-wrap {
    position: relative;
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}

#mapa {
    height: 420px;
    width: 100%;
    z-index: 1;
}

.mapa-leyenda {
    position: absolute;
    bottom: 16px;
    left: 16px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    display: flex;
    gap: 14px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text2);
    z-index: 999;
    box-shadow: var(--shadow);
}

.leyenda-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.dot.azul {
    background: #2563EB;
}

.dot.verde {
    background: #10B981;
}

.dot.gris {
    background: #9CA3AF;
}
</style>