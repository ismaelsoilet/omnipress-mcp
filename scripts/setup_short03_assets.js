const fs = require('fs');
const path = require('path');

const baseDir = '/home/ismaelsoilet/omnipress-mcp';
const pubEp03 = path.join(baseDir, 'public/dossie/ep03');
const visEp03 = path.join(baseDir, 'channels/dossie-historico/media/visuals/ep03');
const voxEp03 = path.join(baseDir, 'channels/dossie-historico/media/voiceover/ep03');
const cutsDir = path.join(baseDir, 'channels/dossie-historico/media/soundtrack/cuts');

[pubEp03, visEp03, voxEp03, cutsDir].forEach(d => {
  fs.mkdirSync(d, { recursive: true });
  console.log('Directorio OK:', d);
});

// Soundtrack
const rawMusic = path.join(baseDir, 'channels/dossie-historico/media/soundtrack/raw/sb_signaltonoise.mp3');
const destPubMusic = path.join(pubEp03, 'short_03_signal_to_noise_track.mp3');
const destCutsMusic = path.join(cutsDir, 'short_03_praga_danca_track.mp3');

if (fs.existsSync(rawMusic)) {
  fs.copyFileSync(rawMusic, destPubMusic);
  fs.copyFileSync(rawMusic, destCutsMusic);
  console.log('Musica copiada:', fs.statSync(destPubMusic).size, 'bytes');
}

// Images
const brainDir = '/home/ismaelsoilet/.gemini/antigravity-ide/brain/c1262941-4ca6-4593-90d3-bcf767426134';
const scenesMap = {
  'carrossel_02_slide1_scene_1791684317773.jpg': 'scene_01_frau_troffea.jpg',
  'carrossel_02_slide2_scene_1791684352205.jpg': 'scene_02_contagio_400.jpg',
  'carrossel_02_slide3_scene_1791684385651.jpg': 'scene_03_orquestra_medica.jpg',
  'carrossel_02_danca_morte_1791662876983.jpg': 'scene_04_danca_morte.jpg',
  'carrossel_02_slide4_scene_1791684424156.jpg': 'scene_05_sapatos_vermelhos.jpg',
  'carrossel_02_slide5_scene_1791684467648.jpg': 'scene_06_histeria_coletiva.jpg',
};

for (const [srcName, dstName] of Object.entries(scenesMap)) {
  let srcP = path.join(brainDir, srcName);
  if (!fs.existsSync(srcP)) {
    srcP = path.join(baseDir, 'channels/dossie-historico/media/carousels', srcName);
  }
  if (fs.existsSync(srcP)) {
    fs.copyFileSync(srcP, path.join(pubEp03, dstName));
    fs.copyFileSync(srcP, path.join(visEp03, dstName));
    console.log('Cena copiada:', dstName, fs.statSync(srcP).size, 'bytes');
  } else {
    console.log('Aviso:', srcName, 'nao encontrada!');
  }
}

console.log('Tudo configurado com sucesso!');
