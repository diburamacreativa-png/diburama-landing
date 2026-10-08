// ─────────────────────────────────────────────────────────────
// CONFIGURACIÓN EDITABLE DEL REEL
// Textos, tiempos, colores y fragmentos de origen.
// Los tiempos se escriben en SEGUNDOS; la salida (out) es exclusiva.
// ─────────────────────────────────────────────────────────────

export const FPS = 25;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION_S = 26;

export const COLORS = {
  light: '#F6F6F4', // blanco cálido
  dark: '#141414', // negro
  accent: '#D52346', // rojo de acento
  // Gris medio para etiquetas sobre fondo claro / oscuro.
  mutedOnLight: 'rgba(20,20,20,0.55)',
  mutedOnDark: 'rgba(246,246,244,0.6)',
};

export const FONTS = {
  display: 'Geist', // pesos 500 y 600
  mono: 'IBM Plex Mono', // etiquetas pequeñas
};

// Archivos originales (carpeta public/media). No se modifican.
export const SOURCES = {
  A: 'media/VIDEO NUEVO MACRISAL 2026_HD_03.mp4', // técnico / isométrico
  B: 'media/Winduu_Final.mp4', // ilustrado / personaje
} as const;

export type SourceId = keyof typeof SOURCES;

export type ClipDef = {src: SourceId; in: number; out: number};

// Fragmentos de origen (segundos desde el inicio de cada archivo).
export const CLIPS = {
  A_intro: {src: 'A', in: 88, out: 90},
  A_dos: {src: 'A', in: 90, out: 92},
  B_dos: {src: 'B', in: 150.6, out: 152.6},
  A_casa: {src: 'A', in: 57, out: 59},
  A_ventana: {src: 'A', in: 70, out: 72},
  B_personaje: {src: 'B', in: 8, out: 10},
  B_mano: {src: 'B', in: 50.2, out: 52.2},
  A_salon: {src: 'A', in: 96, out: 100},
  B_salon: {src: 'B', in: 60, out: 64},
  A_showroom: {src: 'A', in: 108, out: 112},
  B_showroom: {src: 'B', in: 124, out: 128},
  A_final: {src: 'A', in: 88, out: 90},
  B_final: {src: 'B', in: 150.6, out: 152.6},
} satisfies Record<string, ClipDef>;

export type ClipId = keyof typeof CLIPS;

export type Theme = 'light' | 'dark';

export type Segment = {
  id: string;
  from: number; // segundos en el reel
  to: number; // exclusivo
  title: string[]; // una entrada por línea
  kicker: string; // etiqueta mono sobre el título
  theme: Theme;
};

// Guion: el título cambia cuando cambia el texto; si dos segmentos
// consecutivos tienen el mismo título, se mantiene en pantalla.
export const SEGMENTS: Segment[] = [
  {id: 's01', from: 0, to: 2, title: ['Una marca.'], kicker: 'Diburama / Macrisal', theme: 'light'},
  {id: 's02', from: 2, to: 4, title: ['Dos estilos.'], kicker: '01 Isométrico / 02 Ilustrado', theme: 'light'},
  {id: 's03', from: 4, to: 6, title: ['En detalle.'], kicker: '01 / Isométrico', theme: 'light'},
  {id: 's04', from: 6, to: 8, title: ['En detalle.'], kicker: '01 / Isométrico', theme: 'light'},
  {id: 's05', from: 8, to: 10, title: ['Con carácter.'], kicker: '02 / Ilustrado', theme: 'dark'},
  {id: 's06', from: 10, to: 12, title: ['Con carácter.'], kicker: '02 / Ilustrado', theme: 'dark'},
  {id: 's07', from: 12, to: 16, title: ['Mismo espacio.'], kicker: 'Salón / 01 + 02', theme: 'light'},
  {id: 's08', from: 16, to: 20, title: ['Otra mirada.'], kicker: 'Showroom / 01 + 02', theme: 'light'},
  {id: 's09', from: 20, to: 22, title: ['Dos formas', 'de contarlo.'], kicker: '4 planos', theme: 'light'},
  {id: 's10', from: 22, to: 24, title: ['¿Con cuál', 'te quedas?'], kicker: '01 / 02', theme: 'light'},
  {id: 's11', from: 24, to: 26, title: [], kicker: '', theme: 'dark'},
];

// Cierre gráfico.
export const CLOSING = {
  brand: 'Diburama',
  tagline: 'Diseñamos cómo lo cuentas.',
  // Si se dispone del logo real, colócalo en public/ (p. ej. 'logo-diburama.svg')
  // y escribe aquí la ruta. Con null se usa el cierre tipográfico.
  logo: null as string | null,
};

// Etiquetas de las ventanas.
export const CARD_LABELS: Record<SourceId, string> = {
  A: '01 Isométrico',
  B: '02 Ilustrado',
};

// Ritmo de transición (fotogramas).
export const TIMING = {
  card: 10, // movimiento estándar de ventanas
  cardFast: 8,
  titleIn: 10,
  titleOut: 7,
  lineStagger: 3,
  wipe: 10, // cambio de fondo
};

export const sec = (s: number) => Math.round(s * FPS);
