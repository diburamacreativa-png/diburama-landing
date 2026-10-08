// ─────────────────────────────────────────────────────────────
// COREOGRAFÍA DE VENTANAS
// Cada ventana tiene una posición inicial y una lista de movimientos
// (x, y, ancho). La altura siempre es ancho × 9/16, así que la
// proporción 16:9 nunca se deforma.
// `content` indica qué fragmento reproduce y desde qué segundo del reel.
// Los tiempos siguen la rejilla musical (120 BPM): beat(1) = 0,5 s.
// ─────────────────────────────────────────────────────────────
import {ClipId, TIMING, beat} from './config';

export type Rect = {x: number; y: number; w: number};
export type Move = Partial<Rect> & {at: number; dur?: number};

export type CardSpec = {
  id: string;
  life: [number, number]; // segundos en los que la ventana existe
  start: Rect;
  moves: Move[]; // `at` en segundos del reel
  content: {at: number; clip: ClipId; loop?: boolean}[];
  label?: boolean; // etiqueta mono dentro de la ventana
  z?: number;
};

const OFF_R = 1200; // fuera de cuadro por la derecha
const OFF_L = -1100; // fuera de cuadro por la izquierda
const E = beat(0.5); // corchea (0,25 s)
const S = beat(0.25); // semicorchea

// Retículas (px sobre 1080 × 1920), inspiradas en el storyboard:
// ventanas grandes, secundarias que sangran por los bordes.
export const LAYOUT = {
  intro: {x: 120, y: 740, w: 1000}, // sangra 40 px por la derecha
  pairTop: {x: -40, y: 626, w: 880}, // sangra por la izquierda
  pairBottom: {x: 240, y: 1150, w: 880}, // sangra por la derecha; sale de detrás de A
  hero: {x: 60, y: 620, w: 960},
  heroBig: {x: 0, y: 586, w: 1080}, // mismo centro que hero, a sangre
  secondaryR: {x: 600, y: 1250, w: 600}, // sangra por la derecha
  secondaryL: {x: -120, y: 1250, w: 600}, // sangra por la izquierda
  stackTop: {x: 70, y: 584, w: 940},
  stackBottom: {x: 70, y: 1136, w: 940},
  grid: [
    {x: 30, y: 660, w: 500},
    {x: 550, y: 660, w: 500},
    {x: 30, y: 961, w: 500},
    {x: 550, y: 961, w: 500},
  ],
};

export const CARDS: CardSpec[] = [
  // 0–6 s · ventana A: entra por la derecha, se divide en dos y crece como protagonista.
  {
    id: 'A1',
    life: [0, 6.5],
    start: {...LAYOUT.intro, x: 860}, // asoma ya en el primer fotograma
    moves: [
      {at: 0, x: LAYOUT.intro.x, dur: 14},
      {at: 2, ...LAYOUT.pairTop},
      {at: 4, ...LAYOUT.hero},
      {at: 6, x: OFF_L},
    ],
    content: [
      {at: 0, clip: 'A_intro'},
      {at: 2, clip: 'A_dos'},
      {at: 4, clip: 'A_casa'},
    ],
    label: true,
    z: 3,
  },
  // 2–4 s · ventana B: estaba debajo de A y se separa ("se divide en dos").
  {
    id: 'B1',
    life: [2, 4.5],
    start: LAYOUT.intro,
    moves: [
      {at: 2 + S, ...LAYOUT.pairBottom},
      {at: 4, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [{at: 2, clip: 'B_dos'}],
    label: true,
    z: 2,
  },
  // 4–8 s · ventana secundaria (fragmento de la intro A), sangra a la derecha.
  {
    id: 'S1',
    life: [4, 8.5],
    start: {...LAYOUT.secondaryR, x: OFF_R},
    moves: [
      {at: 4 + E, x: LAYOUT.secondaryR.x},
      {at: 6 + E, x: LAYOUT.secondaryR.x - 60, y: LAYOUT.secondaryR.y + 40}, // el conjunto se desplaza
      {at: 8, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [{at: 4, clip: 'A_intro', loop: true}],
    z: 1,
  },
  // 6–8 s · el conjunto se desplaza: entra la ventana técnica.
  {
    id: 'A2',
    life: [6, 8.5],
    start: {...LAYOUT.hero, x: OFF_R},
    moves: [
      {at: 6, x: LAYOUT.hero.x},
      {at: 8, x: OFF_L},
    ],
    content: [{at: 6, clip: 'A_ventana'}],
    label: true,
    z: 3,
  },
  // 8–16 s · ventana B principal: entra lateral, crece con el gesto
  // y pasa a la mitad inferior de la comparación.
  {
    id: 'B2',
    life: [8, 16.5],
    start: {...LAYOUT.hero, x: OFF_R},
    moves: [
      {at: 8, x: LAYOUT.hero.x},
      {at: 11.28, ...LAYOUT.heroBig, dur: 16}, // gesto de la mano (B 51,5–52,1 s)
      {at: 12, ...LAYOUT.stackBottom},
      {at: 16 + S, x: OFF_L},
    ],
    content: [
      {at: 8, clip: 'B_personaje'},
      {at: 10, clip: 'B_mano'},
      {at: 12, clip: 'B_salon'},
    ],
    label: true,
    z: 3,
  },
  // 8–12 s · ventana secundaria (fragmento de la intro B), sangra a la izquierda.
  {
    id: 'S2',
    life: [8, 12.5],
    start: {...LAYOUT.secondaryL, x: OFF_L},
    moves: [
      {at: 8 + E, x: LAYOUT.secondaryL.x},
      {at: 12, x: OFF_L, dur: TIMING.cardFast},
    ],
    content: [{at: 8, clip: 'B_dos', loop: true}],
    z: 1,
  },
  // 12–16 s · salón A, mitad superior.
  {
    id: 'A3',
    life: [12, 16.5],
    start: {...LAYOUT.stackTop, x: OFF_L},
    moves: [
      {at: 12 + S, x: LAYOUT.stackTop.x},
      {at: 16, x: OFF_L},
    ],
    content: [{at: 12, clip: 'A_salon'}],
    label: true,
    z: 3,
  },
  // 16–24 s · showroom A → cuadrícula → comparación final → sale por la izquierda.
  {
    id: 'A4',
    life: [16, 25],
    start: {...LAYOUT.stackTop, x: OFF_R},
    moves: [
      {at: 16, x: LAYOUT.stackTop.x},
      {at: 20, ...LAYOUT.grid[0]},
      {at: 22, ...LAYOUT.stackTop},
      {at: 24, x: OFF_L, dur: TIMING.cardFast},
    ],
    content: [
      {at: 16, clip: 'A_showroom'},
      {at: 20, clip: 'A_casa'},
      {at: 22, clip: 'A_final'},
    ],
    label: true,
    z: 3,
  },
  // 16–24 s · showroom B → cuadrícula → comparación final → sale por la derecha.
  {
    id: 'B3',
    life: [16, 25],
    start: {...LAYOUT.stackBottom, x: OFF_R},
    moves: [
      {at: 16 + S, x: LAYOUT.stackBottom.x},
      {at: 20, ...LAYOUT.grid[2]},
      {at: 22, ...LAYOUT.stackBottom},
      {at: 24, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [
      {at: 16, clip: 'B_showroom'},
      {at: 20, clip: 'B_personaje'},
      {at: 22, clip: 'B_final'},
    ],
    label: true,
    z: 3,
  },
  // 20–22 s · columna derecha de la cuadrícula (entran a semicorcheas).
  {
    id: 'A5',
    life: [20, 22.6],
    start: {...LAYOUT.grid[1], x: OFF_R},
    moves: [
      {at: 20 + S, x: LAYOUT.grid[1].x},
      {at: 22, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [{at: 20, clip: 'A_ventana'}],
    label: true,
    z: 2,
  },
  {
    id: 'B4',
    life: [20, 22.6],
    start: {...LAYOUT.grid[3], x: OFF_R},
    moves: [
      {at: 20 + E, x: LAYOUT.grid[3].x},
      {at: 22, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [{at: 20, clip: 'B_mano'}],
    label: true,
    z: 2,
  },
];

// Números grandes en rojo (segmentos individuales). Entran en el 2.º tiempo.
export const NUMBERS = [
  {text: '01', from: 4 + beat(1), to: 8, x: 64, y: 1236, align: 'left' as const},
  {text: '02', from: 8 + beat(1), to: 12, x: 1020, y: 1236, align: 'right' as const},
];

// Líneas rojas de acento: se dibujan de izquierda a derecha.
export const RULES: {x: number; y: number; w: number; h: number; from: number; to: number | null}[] = [
  {x: 80, y: 618, w: 1000, h: 5, from: beat(1), to: 2}, // intro, bajo el título (sangra a la derecha)
  {x: 70, y: 1121, w: 940, h: 3, from: 14, to: 20}, // costura entre las dos ventanas comparadas
  {x: 80, y: 1262, w: 920, h: 5, from: 24 + beat(1.5), to: null}, // cierre
];

// Periodos con fondo oscuro (barrido de abajo arriba).
export const DARK_RANGES: [number, number][] = [
  [8, 12],
  [24, 26],
];

// Tramos con etiqueta dentro de las ventanas (solo comparaciones A/B).
export const LABEL_RANGES: [number, number][] = [
  [2, 4],
  [12, 24],
];

// Momentos clave del vídeo original que la música subraya.
export const ACCENTS = {
  gesture: 11.8, // la mano llega a cámara (B 52,0 s)
};
