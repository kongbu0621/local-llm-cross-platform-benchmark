import multiprocessing as mp
import os
import time


def main():
    from vllm import LLM, SamplingParams

    model = os.environ["MODEL"]

    print("=== FP8 VLLM SMOKE ATTEMPT 1 ===", flush=True)
    print("model =", model, flush=True)

    t0 = time.time()

    llm = LLM(
        model=model,
        tensor_parallel_size=1,
        max_model_len=32768,
        max_num_seqs=1,
        gpu_memory_utilization=0.85,
        enable_prefix_caching=False,
        enforce_eager=True,
        trust_remote_code=False,
        disable_log_stats=True,
    )

    t1 = time.time()

    sampling = SamplingParams(
        temperature=0.0,
        max_tokens=16,
    )

    outputs = llm.generate(
        ["Reply with the single token sequence: SMOKE_OK"],
        sampling,
    )

    t2 = time.time()

    text = outputs[0].outputs[0].text

    print("load_seconds =", round(t1 - t0, 3), flush=True)
    print("generation_seconds =", round(t2 - t1, 3), flush=True)
    print("output_repr =", repr(text), flush=True)

    if not text:
        print("RESULT=FP8_SMOKE_FAIL empty_output", flush=True)
        raise SystemExit(1)

    print("RESULT=FP8_SMOKE_PASS", flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
