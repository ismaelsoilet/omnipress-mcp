import React from "react";
import { AbsoluteFill, staticFile } from "remotion";

export interface ThumbnailEpisodeProps {
  titleLine1?: string;
  titleLine2?: string;
  tagText?: string;
  calloutText?: string;
  depthTag?: string;
  peopleTag?: string;
  doorTag?: string;
  imageSrc?: string;
  cellarSrc?: string;
  showClassifiedStamp?: boolean;
}

export const ThumbnailEpisode: React.FC<ThumbnailEpisodeProps> = ({
  titleLine1 = "18 ANDARES",
  titleLine2 = "NO SUBSOLO",
  tagText = "ARQUIVO SECRETO // TURQUIA 1963",
  calloutText = "ACHOU ATRÁS DA PAREDE!",
  depthTag = "85 METROS DE PROFUNDIDADE",
  peopleTag = "ABRIGAVA 20.000 PESSOAS",
  doorTag = "PORTAS DE MEIA TONELADA",
  imageSrc = "dossie/ep01/derinkuyu_slide3_corte_transversal_1791756658406.jpg",
  cellarSrc = "dossie/ep01/derinkuyu_slide2_descoberta_1791756631797.jpg",
  showClassifiedStamp = true,
}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#06080C",
        fontFamily: "'Anton', 'Impact', 'Montserrat', sans-serif",
        overflow: "hidden",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Anton&family=Cinzel:wght@800;900&family=Montserrat:wght@800;900&display=swap');
      `}</style>

      {/* 1. Imagem de Fundo Principal: Corte Transversal de Derinkuyu (Lado Direito e Central) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          right: 0,
          width: "72%",
          height: "100%",
          backgroundImage: `url(${staticFile(imageSrc)})`,
          backgroundSize: "cover",
          backgroundPosition: "center 28%",
          filter: "contrast(1.18) saturate(1.15) brightness(0.92)",
        }}
      />

      {/* 2. Composição do Lado Esquerdo: A Descoberta no Porão (Parede Quebrada) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "45%",
          height: "100%",
          backgroundImage: `url(${staticFile(cellarSrc)})`,
          backgroundSize: "cover",
          backgroundPosition: "center 40%",
          filter: "contrast(1.2) brightness(0.55)",
          maskImage: "linear-gradient(to right, black 55%, transparent 100%)",
          WebkitMaskImage: "linear-gradient(to right, black 55%, transparent 100%)",
        }}
      />

      {/* 3. Gradiente Tático Escuro na Esquerda para Contraste Absoluto das Letras */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "60%",
          height: "100%",
          background:
            "linear-gradient(to right, rgba(4, 6, 10, 0.96) 0%, rgba(4, 6, 10, 0.88) 45%, rgba(4, 6, 10, 0.5) 80%, transparent 100%)",
          zIndex: 10,
        }}
      />

      {/* 4. Vinheta de Borda e Efeito de Iluminação Dramática */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          boxShadow: "inset 0 0 140px rgba(0, 0, 0, 0.95), inset 0 0 60px rgba(0, 0, 0, 0.85)",
          pointerEvents: "none",
          zIndex: 15,
        }}
      />

      {/* 5. Linha Dourada de Borda Cinemática */}
      <div
        style={{
          position: "absolute",
          inset: 20,
          border: "2px solid rgba(212, 175, 55, 0.45)",
          borderRadius: 8,
          pointerEvents: "none",
          zIndex: 20,
        }}
      />

      {/* 6. CONTEÚDO PRINCIPAL (LADO ESQUERDO) — LETRAS GIGANTES E LEGENDAS CHAMATIVAS */}
      <div
        style={{
          position: "absolute",
          top: 70,
          left: 75,
          zIndex: 30,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          maxWidth: 950,
        }}
      >
        {/* Badge Superior: Arquivo Desclassificado / Caso Real */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 12,
            backgroundColor: "rgba(10, 12, 16, 0.92)",
            border: "2px solid #D4AF37",
            borderRadius: 8,
            padding: "10px 22px",
            marginBottom: 24,
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.9), 0 0 15px rgba(212, 175, 55, 0.25)",
          }}
        >
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              backgroundColor: "#FF2222",
              boxShadow: "0 0 12px #FF2222, 0 0 20px #FF0000",
            }}
          />
          <span
            style={{
              color: "#FFD700",
              fontFamily: "'Courier New', Courier, monospace",
              fontSize: 22,
              fontWeight: 900,
              letterSpacing: 3.5,
              textTransform: "uppercase",
            }}
          >
            {tagText}
          </span>
        </div>

        {/* Linha 1 de Título Gigante: 18 ANDARES */}
        <h1
          style={{
            margin: 0,
            fontSize: 122,
            lineHeight: 0.95,
            fontWeight: 900,
            fontFamily: "'Anton', 'Impact', sans-serif",
            letterSpacing: 2,
            textTransform: "uppercase",
            color: "#FFE500", // Amarelo vibrante chamativo
            WebkitTextStroke: "4px #000000",
            textShadow: `
              0 0 20px rgba(255, 229, 0, 0.5),
              0 6px 0 #000,
              0 10px 0 #000,
              0 14px 28px rgba(0, 0, 0, 0.95)
            `,
          }}
        >
          {titleLine1}
        </h1>

        {/* Linha 2 de Título Gigante: NO SUBSOLO */}
        <h2
          style={{
            margin: "8px 0 24px 0",
            fontSize: 110,
            lineHeight: 0.95,
            fontWeight: 900,
            fontFamily: "'Anton', 'Impact', sans-serif",
            letterSpacing: 2,
            textTransform: "uppercase",
            color: "#FFFFFF",
            WebkitTextStroke: "4px #000000",
            textShadow: `
              0 6px 0 #000,
              0 10px 0 #000,
              0 14px 28px rgba(0, 0, 0, 0.95)
            `,
          }}
        >
          {titleLine2}
        </h2>

        {/* Sticker / Faixa Chamativa Inclinada: ACHOU ATRÁS DA PAREDE! */}
        <div
          style={{
            transform: "rotate(-3deg)",
            backgroundColor: "#D32F2F", // Vermelho Alerta Vibrante
            border: "3px solid #FFFFFF",
            borderRadius: 10,
            padding: "14px 32px",
            boxShadow: "0 12px 32px rgba(0, 0, 0, 0.9), 0 0 25px rgba(211, 47, 47, 0.6)",
            marginBottom: 32,
          }}
        >
          <span
            style={{
              color: "#FFFFFF",
              fontSize: 42,
              fontWeight: 900,
              fontFamily: "'Montserrat', sans-serif",
              letterSpacing: 1.5,
              textTransform: "uppercase",
              textShadow: "0 3px 6px rgba(0, 0, 0, 0.8)",
            }}
          >
            {calloutText}
          </span>
        </div>

        {/* Mini Dossiê Tático de Metadados de Impacto */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 10,
            backgroundColor: "rgba(6, 8, 12, 0.88)",
            border: "1.5px solid rgba(212, 175, 55, 0.4)",
            borderLeft: "6px solid #D4AF37",
            borderRadius: 8,
            padding: "14px 24px",
            backdropFilter: "blur(10px)",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.75)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ color: "#FFE500", fontSize: 22, fontWeight: 900 }}>▼</span>
            <span
              style={{
                color: "#E2E8F0",
                fontSize: 22,
                fontWeight: 800,
                fontFamily: "'Montserrat', sans-serif",
                letterSpacing: 1,
              }}
            >
              {depthTag}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ color: "#FFE500", fontSize: 22, fontWeight: 900 }}>▼</span>
            <span
              style={{
                color: "#E2E8F0",
                fontSize: 22,
                fontWeight: 800,
                fontFamily: "'Montserrat', sans-serif",
                letterSpacing: 1,
              }}
            >
              {peopleTag}
            </span>
          </div>
        </div>
      </div>

      {/* 7. CARIMBO CONFIDENCIAL NO TOPO DIREITO */}
      {showClassifiedStamp && (
        <div
          style={{
            position: "absolute",
            top: 65,
            right: 75,
            zIndex: 35,
            transform: "rotate(6deg)",
            border: "5px solid #D32F2F",
            borderRadius: 8,
            padding: "8px 26px",
            color: "#D32F2F",
            fontFamily: "'Anton', 'Impact', sans-serif",
            fontSize: 34,
            fontWeight: 900,
            letterSpacing: 5,
            textTransform: "uppercase",
            backgroundColor: "rgba(10, 12, 16, 0.85)",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.85)",
          }}
        >
          CONFIDENCIAL
        </div>
      )}

      {/* 8. ELEMENTO CHAMATIVO INFERIOR DIREITO: DETALHE MAIS ASSUSTADOR */}
      <div
        style={{
          position: "absolute",
          bottom: 70,
          right: 75,
          zIndex: 35,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: 10,
        }}
      >
        {/* Faixa Principal de Alerta: PORTAS DE MEIA TONELADA */}
        <div
          style={{
            backgroundColor: "#FFE500", // Amarelo Ouro Alerta
            border: "3px solid #000000",
            borderRadius: 10,
            padding: "12px 26px",
            boxShadow: "0 12px 30px rgba(0, 0, 0, 0.95)",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          {/* Ícone de Cadeado Tático em SVG Puro */}
          <svg
            width="26"
            height="26"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#000000"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" fill="#000" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span
            style={{
              color: "#000000",
              fontSize: 28,
              fontWeight: 900,
              fontFamily: "'Montserrat', sans-serif",
              letterSpacing: 1.5,
              textTransform: "uppercase",
            }}
          >
            {doorTag}
          </span>
        </div>

        {/* Sub-Sticker Inclinado: SÓ FECHAVAM POR DENTRO */}
        <div
          style={{
            backgroundColor: "#D32F2F",
            color: "#FFFFFF",
            fontFamily: "'Montserrat', sans-serif",
            fontSize: 20,
            fontWeight: 900,
            letterSpacing: 1,
            padding: "6px 18px",
            borderRadius: 6,
            border: "2px solid #FFFFFF",
            boxShadow: "0 6px 16px rgba(0,0,0,0.85)",
            transform: "rotate(-2deg)",
            textTransform: "uppercase",
          }}
        >
          SÓ TRANCAVAM POR DENTRO!
        </div>
      </div>
    </AbsoluteFill>
  );
};
