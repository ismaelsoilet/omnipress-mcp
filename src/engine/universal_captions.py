"""Universal Captions & Subtitles Engine for OmniPress MCP.

Normalizes raw Whisper speech-to-text outputs into synchronized, chunked subtitle
data structures optimized for Remotion video compositions (Shorts, Reels, Documentaries).
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("omnipress.universal_captions")


class UniversalCaptionsEngine:
    """Universal speech-to-text captions aligner and chunker."""

    @staticmethod
    def parse_raw_whisper(whisper_data: Union[str, Path, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts a flat list of word timestamp dictionaries from Whisper JSON outputs."""
        if isinstance(whisper_data, (str, Path)):
            p = Path(whisper_data).resolve()
            if not p.exists():
                raise FileNotFoundError(f"Whisper file not found: {p}")
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            data = whisper_data

        words: List[Dict[str, Any]] = []

        # Case 1: Root contains "words" array directly
        if "words" in data and isinstance(data["words"], list):
            for w in data["words"]:
                word_text = w.get("word") or w.get("text") or ""
                words.append({
                    "word": word_text.strip(),
                    "start": round(float(w.get("start", 0.0)), 3),
                    "end": round(float(w.get("end", 0.0)), 3),
                })
            return words

        # Case 2: Standard OpenAI Whisper with "segments"
        if "segments" in data and isinstance(data["segments"], list):
            for seg in data["segments"]:
                if "words" in seg and isinstance(seg["words"], list):
                    for w in seg["words"]:
                        word_text = w.get("word") or w.get("text") or ""
                        words.append({
                            "word": word_text.strip(),
                            "start": round(float(w.get("start", 0.0)), 3),
                            "end": round(float(w.get("end", 0.0)), 3),
                        })
                else:
                    # Segment without word timestamps: approximate or split
                    seg_text = seg.get("text", "").strip()
                    seg_start = float(seg.get("start", 0.0))
                    seg_end = float(seg.get("end", 0.0))
                    seg_words = seg_text.split()
                    if seg_words:
                        dur_per_word = (seg_end - seg_start) / len(seg_words)
                        for i, term in enumerate(seg_words):
                            w_start = seg_start + i * dur_per_word
                            w_end = w_start + dur_per_word
                            words.append({
                                "word": term.strip(),
                                "start": round(w_start, 3),
                                "end": round(w_end, 3),
                            })
            return words

        # Case 3: Wrapped inside episode/act key (e.g. {"act_01": {"words": [...]}, "act_02": {"words": [...]}})
        nested_words = []
        for val in data.values():
            if isinstance(val, dict):
                act_words = UniversalCaptionsEngine.parse_raw_whisper(val)
                if act_words:
                    nested_words.extend(act_words)
        if nested_words:
            return nested_words

        return words

    @staticmethod
    def chunk_words_for_shorts(
        words: List[Dict[str, Any]],
        words_per_chunk: int = 3,
        max_duration_sec: float = 1.6,
        uppercase: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Groups words into punchy, high-retention chunks for 9:16 vertical video.
        Ensures chunks break naturally at punctuation (. , ! ? :) and do not exceed max_duration.
        """
        if not words:
            return []

        chunks: List[Dict[str, Any]] = []
        current_chunk_words: List[Dict[str, Any]] = []
        chunk_start = words[0]["start"]

        for idx, w in enumerate(words):
            word_str = w["word"].upper() if uppercase else w["word"]
            current_chunk_words.append({
                "word": word_str,
                "start": w["start"],
                "end": w["end"],
            })

            is_punctuation = bool(re.search(r"[.,!?:;]$", w["word"]))
            dur = w["end"] - chunk_start
            reach_limit = len(current_chunk_words) >= words_per_chunk
            is_last = idx == len(words) - 1

            if is_last or reach_limit or (is_punctuation and len(current_chunk_words) >= 2) or dur >= max_duration_sec:
                chunk_text = " ".join(item["word"] for item in current_chunk_words)
                chunk_end = current_chunk_words[-1]["end"]
                chunks.append({
                    "id": len(chunks) + 1,
                    "text": chunk_text,
                    "start": round(chunk_start, 3),
                    "end": round(chunk_end, 3),
                    "duration": round(chunk_end - chunk_start, 3),
                    "words": current_chunk_words,
                })
                current_chunk_words = []
                if not is_last:
                    chunk_start = words[idx + 1]["start"]

        return chunks

    @staticmethod
    def verify_timeline(
        payload: Dict[str, Any],
        min_gap: float = 0.08,
        max_gap: float = 1.6,
        max_chunk: float = 1.6,
    ) -> Dict[str, Any]:
        """Lints caption chunks and word timings before rendering.

        Returns errors (blocking), warnings (retention risks) and stats.
        """
        words = payload.get("words") or []
        chunks = payload.get("chunks") or []
        errors: List[str] = []
        warnings: List[str] = []
        gaps: List[float] = []

        for idx, word in enumerate(words):
            start = float(word.get("start", 0.0))
            end = float(word.get("end", 0.0))
            if end < start - 1e-6:
                errors.append(f"word {idx} has negative duration ({start} -> {end})")
            if idx and start < float(words[idx - 1].get("end", 0.0)) - 0.001:
                errors.append(f"word {idx} overlaps the previous word")

        for idx, chunk in enumerate(chunks):
            start = float(chunk.get("start", 0.0))
            end = float(chunk.get("end", 0.0))
            duration = end - start
            if not str(chunk.get("text", "")).strip():
                errors.append(f"chunk {idx + 1} is empty")
            if duration <= 0:
                errors.append(f"chunk {idx + 1} has non-positive duration ({duration})")
            elif duration > max_chunk + 1e-6:
                errors.append(
                    f"chunk {idx + 1} lasts {duration:.3f}s (max {max_chunk:.2f}s)"
                )
            if idx:
                gap = start - float(chunks[idx - 1].get("end", 0.0))
                gaps.append(gap)
                if gap < -0.001:
                    errors.append(f"chunk {idx + 1} overlaps the previous chunk")
                elif gap < min_gap:
                    warnings.append(
                        f"chunk {idx + 1} gap is {gap:.3f}s (< {min_gap:.2f}s); may cause flicker"
                    )
                elif gap > max_gap:
                    warnings.append(
                        f"chunk {idx + 1} gap is {gap:.3f}s (> {max_gap:.2f}s); captions disappear"
                    )

        total_duration = float(words[-1]["end"]) if words else 0.0
        avg_chunk = (
            sum(float(c.get("end", 0.0)) - float(c.get("start", 0.0)) for c in chunks) / len(chunks)
            if chunks
            else 0.0
        )
        return {
            "success": not errors,
            "errors": errors,
            "warnings": warnings,
            "stats": {
                "words": len(words),
                "chunks": len(chunks),
                "duration_seconds": round(total_duration, 3),
                "average_chunk_seconds": round(avg_chunk, 3),
                "min_gap_seconds": round(min(gaps), 3) if gaps else None,
                "max_gap_seconds": round(max(gaps), 3) if gaps else None,
            },
        }

    def process_and_export(
        self,
        input_whisper: Union[str, Path, Dict[str, Any]],
        output_json: Union[str, Path],
        words_per_chunk: int = 3,
        uppercase: bool = True,
        act_id: str = "short_01",
        verify: bool = False,
        min_gap: float = 0.08,
        max_gap: float = 1.6,
        max_chunk: float = 1.6,
    ) -> Dict[str, Any]:
        """Loads Whisper input, chunks words, and exports Remotion-ready caption JSON.
        
        Writes both flat root keys (metadata, words, chunks) and act-keyed dictionary (e.g. ['short_01']),
        ensuring 100% compatibility with Remotion components (SynchronizedCaptions, WordByWordCaptions)
        as well as legacy scripts and channel utilities.
        """
        out_path = Path(output_json).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        raw_words = self.parse_raw_whisper(input_whisper)
        chunks = self.chunk_words_for_shorts(
            words=raw_words,
            words_per_chunk=words_per_chunk,
            uppercase=uppercase,
        )

        total_duration = raw_words[-1]["end"] if raw_words else 0.0
        act_data = {
            "name": act_id,
            "duration": total_duration,
            "words": raw_words,
            "chunks": chunks,
        }
        payload = {
            "metadata": {
                "total_words": len(raw_words),
                "total_chunks": len(chunks),
                "duration_seconds": total_duration,
                "act_id": act_id,
            },
            "words": raw_words,
            "chunks": chunks,
            act_id: act_data,
        }

        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        result = {
            "success": True,
            "output_file": str(out_path),
            "act_id": act_id,
            "total_words": len(raw_words),
            "total_chunks": len(chunks),
            "duration": total_duration,
        }
        if verify:
            verification = self.verify_timeline(
                payload, min_gap=min_gap, max_gap=max_gap, max_chunk=max_chunk
            )
            result["verification"] = verification
            result["verification_success"] = verification["success"]
        return result
