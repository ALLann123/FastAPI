#!/usr/bin/python3
import time
import numpy as np
import sherpa_onnx


class KrokoSTT:
    """German streaming STT using the kroko Zipformer2 transducer"""
    TARGET_SR=16000 #kroko expects 16kHz

    def __init__(self, model_dir:str="model", num_threads:int=4):
        print("Loading Kroko German model....")

        t0=time.perf_counter()

        self.recognizer=sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=f"{model_dir}/tokens.txt",
            encoder=f"{model_dir}/encoder.onnx",
            decoder=f"{model_dir}/decoder.onnx",
            joiner=f"{model_dir}/joiner.onnx",
            num_threads=num_threads,
            sample_rate=self.TARGET_SR,
            feature_dim=80,
            decoding_method="greedy_search",
            provider="cpu",
        )
        print(f"Model loaded in {time.perf_counter()-t0:.2f}s")


    def _resample_if_needed(self, audio:np.ndarray, sr:int)->np.array:
        """Linear resample to 16kHz if the source isn't already 16kHZ"""
        if sr==self.TARGET_SR:
            return audio

        # simple linear interpolation--good enough for speech
        duration = len(audio) / sr
        n_target = int(duration * self.TARGET_SR)
        x_old = np.linspace(0.0, duration, num=len(audio), endpoint=False)
        x_new = np.linspace(0.0, duration, num=n_target, endpoint=False)
        return np.interp(x_new, x_old, audio).astype(np.float32)

    def transcribe(self, audio: np.ndarray, sample_rate:int)-> str:
        """Transcribe a mono float32 waveform."""
        audio = self._resample_if_needed(audio, sample_rate)

        stream = self.recognizer.create_stream()
        stream.accept_waveform(self.TARGET_SR, audio)
        # 0.66 s of silence so the trailing word(s) get decoded
        stream.accept_waveform(
            self.TARGET_SR,
            np.zeros(int(0.66 * self.TARGET_SR), dtype=np.float32),
        )
        stream.input_finished()

        while self.recognizer.is_ready(stream):
            self.recognizer.decode_streams([stream])

        result = self.recognizer.get_result(stream)
        # sherpa-onnx API changed: newer returns str, older returns obj.text
        return result.text if hasattr(result, "text") else str(result)
    