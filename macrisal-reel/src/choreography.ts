// ─────────────────────────────────────────────────────────────
// COREOGRAFÍA DE VENTANAS
// Cada ventana tiene una posición inicial y una lista de movimientos
// (x, y, ancho). La altura siempre es ancho × 9/16, así que la
// proporción 16:9 nunca se deforma.
// `content` indica qué fragmento reproduce y desde qué segundo del reel.
// ─────────────────────────────────────────────────────────────
import {ClipId, TIMING} from './config';

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

// Retículas (px sobre 1080 × 1920).
const L = 80; // margen izquierdo, alineado con el título
const OFF_R = 1180; // fuera de cuadro por la derecha
const OFF_L = -1000; // fuera de cuadro por la izquierda

export const LAYOUT = {
  intro: {x: L, y: 560, w: 920},
  pairTop: {x: L, y: 480, w: 760},
  pairBottom: {x: 240, y: 935, w: 760},
  hero: {x: L, y: 480, w: 920},
  heroBig: {x: 20, y: 446, w: 1040}, // mismo centro que hero, más grande
  secondaryR: {x: 600, y: 1070, w: 400},
  secondaryL: {x: L, y: 1070, w: 400},
  stackTop: {x: L, y: 450, w: 900},
  stackBottom: {x: L, y: 980, w: 900},
  grid: [
    {x: L, y: 590, w: 448},
    {x: 552, y: 590, w: 448},
    {x: L, y: 866, w: 448},
    {x: 552, y: 866, w: 448},
  ],
  finalTop: {x: L, y: 585, w: 760},
  finalBottom: {x: 240, y: 1040, w: 760},
};

const T = TIMING.card;
const F = 1 / 25; // un fotograma en segundos

export const CARDS: CardSpec[] = [
  // 0–4 s · ventana A: entra por la derecha y después se convierte en la mitad superior.
  {
    id: 'A1',
    life: [0, 6.5],
    start: {...LAYOUT.intro, x: 860}, // asoma ya en el primer fotograma
    moves: [
      {at: 0, x: L, dur: 14},
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
  // 2–4 s · ventana B: se separa de A ("se divide en dos").
  {
    id: 'B1',
    life: [2, 4.5],
    start: LAYOUT.intro,
    moves: [
      {at: 2 + 2 * F, ...LAYOUT.pairBottom},
      {at: 4, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [{at: 2, clip: 'B_dos'}],
    label: true,
    z: 2,
  },
  // 4–8 s · ventana secundaria con el fragmento de la intro (A).
  {
    id: 'S1',
    life: [4, 8.5],
    start: {...LAYOUT.secondaryR, x: OFF_R},
    moves: [
      {at: 4 + 8 * F, x: LAYOUT.secondaryR.x},
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
      {at: 6, x: L},
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
      {at: 8, x: L},
      {at: 11.28, ...LAYOUT.heroBig, dur: 16}, // gesto de la mano (B 51,5–52,1 s)
      {at: 12, ...LAYOUT.stackBottom},
      {at: 16 + 3 * F, x: OFF_L},
    ],
    content: [
      {at: 8, clip: 'B_personaje'},
      {at: 10, clip: 'B_mano'},
      {at: 12, clip: 'B_salon'},
    ],
    label: true,
    z: 3,
  },
  // 8–12 s · ventana secundaria con el fragmento de la intro (B).
  {
    id: 'S2',
    life: [8, 12.5],
    start: {...LAYOUT.secondaryL, x: OFF_L},
    moves: [
      {at: 8 + 8 * F, x: L},
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
      {at: 12 + 2 * F, x: L},
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
      {at: 16, x: L},
      {at: 20, ...LAYOUT.grid[0]},
      {at: 22, ...LAYOUT.finalTop},
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
      {at: 16 + 3 * F, x: L},
      {at: 20, ...LAYOUT.grid[2]},
      {at: 22, ...LAYOUT.finalBottom},
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
  // 20–22 s · columna derecha de la cuadrícula.
  {
    id: 'A5',
    life: [20, 22.6],
    start: {...LAYOUT.grid[1], x: OFF_R},
    moves: [
      {at: 20 + 3 * F, x: LAYOUT.grid[1].x},
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
      {at: 20 + 6 * F, x: LAYOUT.grid[3].x},
      {at: 22, x: OFF_R, dur: TIMING.cardFast},
    ],
    content: [{at: 20, clip: 'B_mano'}],
    label: true,
    z: 2,
  },
];

// Números grandes en rojo (segmentos individuales).
export const NUMBERS = [
  {text: '01', from: 4 + 4 * F, to: 8, x: L, y: 1066, align: 'left' as const},
  {text: '02', from: 8 + 4 * F, to: 12, x: 1000, y: 1066, align: 'right' as const},
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
