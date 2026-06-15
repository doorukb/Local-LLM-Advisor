from __future__ import annotations
import customtkinter as ctk

INFERENCE_ENGINES = ("Ollama", "llama.cpp", "LM Studio")
PRIMARY_USE_CASES = (
    "General chat",
    "Coding assistant",
    "Document Q&A",
    "Creative writing",
    "Summarization",
)

# get the user's selections from the dropdown menus
def get_selections(engine_combo: ctk.CTkComboBox, use_case_combo: ctk.CTkComboBox) -> dict[str, str]:
    return {
        "inference_engine": engine_combo.get(),
        "primary_use_case": use_case_combo.get(),
    }

# open the main window and block until the user closes it
def run_gui() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.title("Local LLM Advisor")
    window.geometry("800x700")
    window.minsize(640, 560)

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=0)
    window.grid_rowconfigure(1, weight=1)

    input_frame = ctk.CTkFrame(window, fg_color="transparent")
    input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
    input_frame.grid_columnconfigure(1, weight=1)

    engine_label = ctk.CTkLabel(input_frame, text="Inference engine")
    engine_label.grid(row=0, column=0, sticky="w", padx=(0, 12), pady=8)

    engine_combo = ctk.CTkComboBox(input_frame, values=list(INFERENCE_ENGINES), state="readonly")
    engine_combo.set(INFERENCE_ENGINES[0])
    engine_combo.grid(row=0, column=1, sticky="ew", pady=8)

    use_case_label = ctk.CTkLabel(input_frame, text="Primary use case")
    use_case_label.grid(row=1, column=0, sticky="w", padx=(0, 12), pady=8)

    use_case_combo = ctk.CTkComboBox(input_frame,values=list(PRIMARY_USE_CASES), state="readonly")
    use_case_combo.set(PRIMARY_USE_CASES[0])
    use_case_combo.grid(row=1, column=1, sticky="ew", pady=8)

    window.mainloop()

if __name__ == "__main__":
    run_gui()