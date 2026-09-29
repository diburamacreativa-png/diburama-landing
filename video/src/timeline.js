// TIMELINE MAESTRO — cada escena es un componente independiente con [start, end) en segundos.
import { scene01 } from './scenes/s01_blueprint.js';
import { scene02 } from './scenes/s02_machine.js';
import { scene03 } from './scenes/s03_software.js';
import { scene04 } from './scenes/s04_horizon.js';
import { scene05, scene06 } from './scenes/s05_person.js';
import { scene07, scene08 } from './scenes/s07_reveal.js';
export const TIMELINE = [scene01, scene02, scene03, scene04, scene05, scene06, scene07, scene08];
