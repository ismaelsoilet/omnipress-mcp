import { Config } from "@remotion/cli/config";

// 1. Formato e compressão de frames intermediários (JPEG otimizado para velocidade e I/O)
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(80);
Config.setOverwriteOutput(true);
Config.setCodec("h264");
Config.setCrf(20);

// 2. Cache persistente de compilação (elimina 7-9s de recompilação do Webpack)
Config.setCachingEnabled(true);

// 3. Encoder FFmpeg em preset "fast" (codificação muito mais ágil)
Config.setX264Preset("fast");

// 4. Multi-processamento no Linux (distribuição equilibrada nos cores da CPU)
Config.setChromiumMultiProcessOnLinux(true);

// 5. Concorrência calibrada para a memória livre da máquina (evita swap de disco)
Config.setConcurrency(4);

