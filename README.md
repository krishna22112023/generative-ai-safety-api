# Guardrails for AI safety and reliability

Guardrails for AI Safety and Reliability is a modular API designed to help teams implement AI safety best practices out-of-the-box. This project provides a unified interface for running safety and reliability checks on generative AI outputs, making it easy to integrate robust guardrails into any in-house GenAI product.

**Key Features:**
- **Plug-and-play API:** Easily connect the guardrail API to any generative AI system you develop, regardless of model or platform.
- **Comprehensive Safety Checks:** Automatically screen for toxicity, bias, PII (personally identifiable information), and secret leakage using state-of-the-art tools and configurable rules.
- **Production-Ready:** Run safety and reliability tests both before and during production to ensure outputs meet organizational and regulatory standards.
- **Configurable & Extensible:** Customize guardrails and thresholds to fit your use case, and extend with new rules as needed.

This project helps you ship safer, more reliable AI applications with minimal effort, so you can focus on building value while reducing risk.

![Workflow Diagram](assets/workflow.jpg)

The above diagram illustrates the end-to-end workflow of the Guardrails for AI Safety and Reliability API. The process begins with the ingestion of user input which is first passed through **Input Guardrails** that perform the following checks : 
- **Toxicity:** Detects and flags toxic, obscene, threatening, insulting, or sexually explicit language.
- **Bias:** Identifies and scores identity-based attacks or biased content.
- **Privacy:** Checks for the presence of personally identifiable information (PII) and secret leakage.
- **Prompt Attack:** Detects prompt injection attempts, jailbreaks, and other adversarial manipulations.
- **Topic Relevance:** Ensures the response is relevant to the intended topic or context.

After the model generates a response, the **Output Guardrails** perform the following checks : 
- **Alignment:** Assesses whether the model output aligns with ethical, moral, and intended goals.
- **Code Safety:** Checks generated code for unsafe, vulnerable, or harmful content and rates its severity.
- **Formatting:** Validates that outputs are well-formed (e.g., valid JSON, SQL, or CLI syntax).


## Setup

To set up the [uv](https://github.com/astral-sh/uv) package manager, follow these steps:

1. **Install uv**

   You can install `uv` using the recommended method for your operating system.

   - **On Linux/macOS (using shell):**
     ```sh
     curl -Ls https://astral.sh/uv/install.sh | sh
     ```
     This will download and install the latest version of `uv` to `~/.cargo/bin/uv` or another location in your `$PATH`.

   - **On Windows (using PowerShell):**
     ```powershell
     iwr https://astral.sh/uv/install.ps1 -useb | iex
     ```

   - **Alternatively, with pipx:**
     ```sh
     pipx install uv
     ```

2. **Verify the installation**

   After installation, check that `uv` is available:
   ```sh
   uv --version
   ```

3. **(Optional) Add uv to your PATH**

   If the `uv` command is not found, ensure that the installation directory (e.g., `~/.cargo/bin` or the directory shown in the install output) is in your system's `PATH`.

4. **Use uv to manage dependencies**

   - To install dependencies from `pyproject.toml`:
     ```sh
     uv pip install --require-locked
     ```

   - To create a lockfile:
     ```sh
     uv pip compile pyproject.toml
     ```

   - For more commands and usage, see the [uv documentation](https://github.com/astral-sh/uv).
