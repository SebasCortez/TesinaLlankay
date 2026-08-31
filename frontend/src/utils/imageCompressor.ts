/**
 * Utilidad de compresión y optimización de imágenes en el cliente (Browser Canvas API)
 * Reduce el peso de imágenes (JPEG, PNG, WebP) hasta en un 80-90% antes del envío a la API
 */

export interface CompressionOptions {
  maxWidth?: number
  maxHeight?: number
  quality?: number // 0.1 a 1.0
  format?: 'image/webp' | 'image/jpeg' | 'image/png'
}

export interface CompressionResult {
  file: File
  blob: Blob
  dataUrl: string
  originalSize: number
  compressedSize: number
  compressionRatio: number // Porcentaje de ahorro
}

/**
 * Comprime un archivo de imagen utilizando Canvas API
 * @param file Archivo original seleccionado por el usuario
 * @param options Opciones de compresión (maxWidth, maxHeight, quality, format)
 * @returns Promesa con los datos del archivo optimizado
 */
export async function comprimirImagen(
  file: File,
  options: CompressionOptions = {}
): Promise<CompressionResult> {
  const {
    maxWidth = 1200,
    maxHeight = 1200,
    quality = 0.82,
    format = 'image/webp'
  } = options

  // Si no es imagen, retornar tal cual
  if (!file.type.startsWith('image/')) {
    throw new Error('El archivo proporcionado no es una imagen válida.')
  }

  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      const img = new Image()

      img.onload = () => {
        let width = img.width
        let height = img.height

        // Calcular nuevas dimensiones conservando aspect ratio
        if (width > maxWidth || height > maxHeight) {
          if (width / height > maxWidth / maxHeight) {
            height = Math.round((height * maxWidth) / width)
            width = maxWidth
          } else {
            width = Math.round((width * maxHeight) / height)
            maxHeight ? (height = maxHeight) : null
          }
        }

        // Crear canvas
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height

        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('No se pudo inicializar el contexto de canvas 2D.'))
          return
        }

        // Dibujar con suavizado de alta calidad
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        ctx.drawImage(img, 0, 0, width, height)

        // Convertir a blob
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('Error al generar el Blob de la imagen comprimida.'))
              return
            }

            // Generar nuevo nombre de archivo
            const extension = format === 'image/webp' ? '.webp' : format === 'image/jpeg' ? '.jpg' : '.png'
            const baseName = file.name.replace(/\.[^/.]+$/, '')
            const newFileName = `${baseName}_opt${extension}`

            const compressedFile = new File([blob], newFileName, {
              type: format,
              lastModified: Date.now()
            })

            const dataUrl = canvas.toDataURL(format, quality)
            const originalSize = file.size
            const compressedSize = blob.size
            const compressionRatio = Math.round(((originalSize - compressedSize) / originalSize) * 100)

            resolve({
              file: compressedFile,
              blob,
              dataUrl,
              originalSize,
              compressedSize,
              compressionRatio: Math.max(0, compressionRatio)
            })
          },
          format,
          quality
        )
      }

      img.onerror = () => {
        reject(new Error('No se pudo cargar la imagen para compresión.'))
      }

      img.src = e.target?.result as string
    }

    reader.onerror = () => {
      reject(new Error('Error al leer el archivo de imagen.'))
    }

    reader.readAsDataURL(file)
  })
}

/**
 * Formatea bytes a tamaño legible (KB / MB)
 */
export function formatearBytes(bytes: number, decimals = 1): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}
