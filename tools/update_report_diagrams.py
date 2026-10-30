import re
import os

def update_chapter3():
    path = "tools/report_modules/chapter3.py"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Update policy hierarchy figure
    old_hier = r"""\begin{figure}[H]
    \centering
    \IfFileExists{results/policy_confusion_matrix.png}{\includegraphics[width=0.62\textwidth]{results/policy_confusion_matrix.png}}{%
        \fbox{\parbox{0.60\textwidth}{\centering \textbf{[SafeAd AI Four-Tier Regulatory Policy Hierarchy]}}}%
    }
    \caption{The SafeAd AI Content Policy Taxonomy and Decision Escalation Flow.}
    \label{fig:policy_hierarchy}
\end{figure}"""

    new_hier = r"""\begin{figure}[H]
    \centering
    \IfFileExists{policy_hierarchy.png}{\includegraphics[width=0.96\textwidth]{policy_hierarchy.png}}{%
        \IfFileExists{overleaf_figures/policy_hierarchy.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/policy_hierarchy.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{SafeAd AI Four-Tier Regulatory Policy Hierarchy}}}}%
    }
    \caption{The SafeAd AI Four-Tier Content Policy Taxonomy, Statutory Grounding, and Enforcement Escalation Flow.}
    \label{fig:policy_hierarchy}
\end{figure}"""
    c = c.replace(old_hier, new_hier)

    # 2. Replace Category 1 sample figure
    old_sfa_fig = r"""\subsubsection{Concrete Test Case Walkthrough with Illustrative Figures}
Figure~\ref{fig:sample_sfa} illustrates an authentic commercial advertisement belonging to the \texttt{SAFE\_FOR\_ALL} category (\texttt{safe\_python\_ad.jpg} and \texttt{apples\_ad.jpg}).

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{sample_ad_media/apples_ad.jpg}{\includegraphics[width=0.92\textwidth]{sample_ad_media/apples_ad.jpg}}{%
            \IfFileExists{apples_ad.jpg}{\includegraphics[width=0.92\textwidth]{apples_ad.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Apples Ad (SAFE\_FOR\_ALL)}}}}%
        }
        \caption{Consumer Grocery Promotion (\texttt{apples\_ad.jpg})}
        \label{fig:sfa_apples}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{joseph_safead_core/backend2jb/datasets/samples/safe_python_ad.jpg}{\includegraphics[width=0.92\textwidth]{joseph_safead_core/backend2jb/datasets/samples/safe_python_ad.jpg}}{%
            \IfFileExists{safe_python_ad.jpg}{\includegraphics[width=0.92\textwidth]{safe_python_ad.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Python Course Ad (SAFE\_FOR\_ALL)}}}}%
        }
        \caption{Educational Software Ad (\texttt{safe\_python\_ad.jpg})}
        \label{fig:sfa_python}
    \end{subfigure}
    \caption{Representative \texttt{SAFE\_FOR\_ALL} Commercial Advertisements.}
    \label{fig:sample_sfa}
\end{figure}"""

    new_sfa_fig = r"""\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To evaluate the operational behavior of the \texttt{SAFE\_FOR\_ALL} policy specification, the pipeline processes commercial media assets such as organic grocery promotions and introductory software programming courses (\texttt{apples\_ad.jpg} and \texttt{safe\_python\_ad.jpg})."""
    c = c.replace(old_sfa_fig, new_sfa_fig)

    # 3. Replace Category 2 sample figure
    old_s14_fig = r"""\subsubsection{Concrete Test Case Walkthrough with Illustrative Figures}
Figure~\ref{fig:sample_s14p} depicts representative commercial items evaluated under the \texttt{SAFE\_14\_PLUS} policy tier.

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{joseph_safead_core/backend2jb/datasets/samples/violence_combat_ad.jpg}{\includegraphics[width=0.92\textwidth]{joseph_safead_core/backend2jb/datasets/samples/violence_combat_ad.jpg}}{%
            \IfFileExists{violence_combat_ad.jpg}{\includegraphics[width=0.92\textwidth]{violence_combat_ad.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Action Sports/Gaming Ad}}}}%
        }
        \caption{Stylized Martial Arts / Gaming Ad}
        \label{fig:s14_combat}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \fbox{\parbox{0.80\textwidth}{\centering \textbf{[Lacrosse Attack Stick / High-Caffeine Energy Drink]}\\[0.3cm]\small Sample ID: \texttt{SAFEAD\_S14P\_IMG\_050}\\Youth athletic gear with intense competitive copy.}}
        \caption{Youth Athletic Gear Promotion}
        \label{fig:s14_lacrosse}
    \end{subfigure}
    \caption{Representative \texttt{SAFE\_14\_PLUS} Adolescent Commercial Advertisements.}
    \label{fig:sample_s14p}
\end{figure}"""

    new_s14_fig = r"""\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To evaluate adolescent boundary arbitration, the pipeline assesses commercial items such as competitive action athletics paired with high-caffeine energy drink branding (\texttt{SAFEAD\_S14P\_IMG\_050} and \texttt{violence\_combat\_ad.jpg})."""
    c = c.replace(old_s14_fig, new_s14_fig)

    # 4. Replace Category 3 sample figure
    old_s18_fig = r"""\subsubsection{Concrete Test Case Walkthrough with Illustrative Figures}
Figure~\ref{fig:sample_s18p} illustrates authentic commercial advertisements belonging to the \texttt{SAFE\_18\_PLUS} category (\texttt{beer\_pub.jpg} and \texttt{adult\_dating.jpg}).

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{sample_ad_media/beer_pub.jpg}{\includegraphics[width=0.92\textwidth]{sample_ad_media/beer_pub.jpg}}{%
            \IfFileExists{beer_pub.jpg}{\includegraphics[width=0.92\textwidth]{beer_pub.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Beer Pub Ad (SAFE\_18\_PLUS)}}}}%
        }
        \caption{Commercial Brewery \& Pub Ad (\texttt{beer\_pub.jpg})}
        \label{fig:s18_beer}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{sample_ad_media/adult_dating.jpg}{\includegraphics[width=0.92\textwidth]{sample_ad_media/adult_dating.jpg}}{%
            \IfFileExists{adult_dating.jpg}{\includegraphics[width=0.92\textwidth]{adult_dating.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Adult Dating Ad (SAFE\_18\_PLUS)}}}}%
        }
        \caption{Adult Social Matchmaking (\texttt{adult\_dating.jpg})}
        \label{fig:s18_dating}
    \end{subfigure}
    \caption{Representative \texttt{SAFE\_18\_PLUS} Adult-Restricted Commercial Advertisements.}
    \label{fig:sample_s18p}
\end{figure}"""

    new_s18_fig = r"""\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To analyze mature commercial gating, the framework evaluates licensed craft brewery promotions and consensual matchmaking advertisements (\texttt{beer\_pub.jpg} and \texttt{adult\_dating.jpg})."""
    c = c.replace(old_s18_fig, new_s18_fig)

    # 5. Replace Category 4 sample figure
    old_ufa_fig = r"""\subsubsection{Concrete Test Case Walkthrough with Illustrative Figures}
Figure~\ref{fig:sample_ufa} illustrates authentic prohibited advertisements evaluated under the \texttt{UNSAFE\_FOR\_ALL} category (\texttt{lucky\_draw.jpg} and \texttt{scam\_paisa\_double\_ad.jpg}).

\begin{figure}[H]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{sample_ad_media/lucky_draw.jpg}{\includegraphics[width=0.92\textwidth]{sample_ad_media/lucky_draw.jpg}}{%
            \IfFileExists{lucky_draw.jpg}{\includegraphics[width=0.92\textwidth]{lucky_draw.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Predatory Lottery Scam Ad}}}}%
        }
        \caption{Predatory Lucky Draw Scam (\texttt{lucky\_draw.jpg})}
        \label{fig:ufa_lottery}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \IfFileExists{joseph_safead_core/backend2jb/datasets/samples/scam_paisa_double_ad.jpg}{\includegraphics[width=0.92\textwidth]{joseph_safead_core/backend2jb/datasets/samples/scam_paisa_double_ad.jpg}}{%
            \IfFileExists{scam_paisa_double_ad.jpg}{\includegraphics[width=0.92\textwidth]{scam_paisa_double_ad.jpg}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Paisa Double Scam Ad}}}}%
        }
        \caption{Guaranteed Returns Fraud (\texttt{scam\_paisa\_double\_ad.jpg})}
        \label{fig:ufa_scam}
    \end{subfigure}
    \caption{Representative \texttt{UNSAFE\_FOR\_ALL} Universally Prohibited Advertisements.}
    \label{fig:sample_ufa}
\end{figure}"""

    new_ufa_fig = r"""\subsubsection{Forensic Test Case Walkthrough and Scoring Trace}
To analyze pre-publication threat interception, the framework processes fraudulent marketing samples including predatory lottery schemes and high-yield Ponzi operations (\texttt{lucky\_draw.jpg} and \texttt{scam\_paisa\_double\_ad.jpg})."""
    c = c.replace(old_ufa_fig, new_ufa_fig)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Chapter 3 successfully updated: dataset sample figures removed, policy hierarchy diagram integrated!")

def update_chapter5():
    path = "tools/report_modules/chapter5.py"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Add multimodal_feature_pipeline.png before Algorithm 2
    old_ch5_fusion = r"""\section{Mathematical Formulation of Evidence Fusion}"""
    new_ch5_fusion = r"""\section{Mathematical Formulation of Evidence Fusion}

Figure~\ref{fig:multimodal_pipeline} illustrates the synthesis of multimodal feature streams into the 33-dimensional feature representation and non-linear risk escalation score.

\begin{figure}[H]
    \centering
    \IfFileExists{multimodal_feature_pipeline.png}{\includegraphics[width=0.96\textwidth]{multimodal_feature_pipeline.png}}{%
        \IfFileExists{overleaf_figures/multimodal_feature_pipeline.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/multimodal_feature_pipeline.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Multimodal Evidence Extraction and Risk Escalation Architecture}}}}%
    }
    \caption{Multimodal Evidence Extraction, Vectorization into 33-D Representation, and Non-Linear Risk Escalation Architecture.}
    \label{fig:multimodal_pipeline}
\end{figure}"""
    if old_ch5_fusion in c and "fig:multimodal_pipeline" not in c:
        c = c.replace(old_ch5_fusion, new_ch5_fusion)

    # Add fusion_pipeline.png right after Strategy D
    old_strat_d = r"""Strategy D establishes a hierarchical safety protocol that fuses Qwen3-VL semantic reasoning with Random Forest tabular predictions. The protocol is formalized in Algorithm~\ref{alg:fusion}."""
    new_strat_d = r"""Strategy D establishes a hierarchical safety protocol that fuses Qwen3-VL semantic reasoning with Random Forest tabular predictions. The protocol is formalized in Algorithm~\ref{alg:fusion} and visually diagrammed in Figure~\ref{fig:fusion_flowchart}.

\begin{figure}[H]
    \centering
    \IfFileExists{fusion_pipeline.png}{\includegraphics[width=0.96\textwidth]{fusion_pipeline.png}}{%
        \IfFileExists{overleaf_figures/fusion_pipeline.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/fusion_pipeline.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Strategy D Hierarchical Safety Fusion Protocol Flowchart}}}}%
    }
    \caption{Strategy D Hierarchical Safety Fusion Protocol: Arbitration Logic between Qwen3-VL Zero-Tolerance Safety Veto and Random Forest Tabular Prediction.}
    \label{fig:fusion_flowchart}
\end{figure}"""
    if old_strat_d in c and "fig:fusion_flowchart" not in c:
        c = c.replace(old_strat_d, new_strat_d)

    # Add vision_engine_concurrency.png right after DirectShow concurrency
    old_engine = r"""Algorithm~\ref{alg:engine} details this implementation."""
    new_engine = r"""Figure~\ref{fig:vision_concurrency} details the decoupled thread architecture of the \texttt{Realtime30FPSVisionEngine}, illustrating how DirectShow frame ingestion is separated from downstream AI inference to guarantee stable 30 FPS playback. Algorithm~\ref{alg:engine} formalizes the underlying Python concurrency implementation.

\begin{figure}[H]
    \centering
    \IfFileExists{vision_engine_concurrency.png}{\includegraphics[width=0.96\textwidth]{vision_engine_concurrency.png}}{%
        \IfFileExists{overleaf_figures/vision_engine_concurrency.png}{\includegraphics[width=0.96\textwidth]{overleaf_figures/vision_engine_concurrency.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Realtime30FPSVisionEngine Decoupled DirectShow Concurrency Blueprint}}}}%
    }
    \caption{Realtime30FPSVisionEngine Decoupled Thread Architecture: Isolation of DirectShow COM STA Polling Thread from Downstream Deep Learning Workers to Eliminate Native Heap Corruption.}
    \label{fig:vision_concurrency}
\end{figure}"""
    if old_engine in c and "fig:vision_concurrency" not in c:
        c = c.replace(old_engine, new_engine)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Chapter 5 successfully updated: multimodal pipeline, fusion flowchart, and concurrency diagrams integrated!")

def update_chapter6():
    path = "tools/report_modules/chapter6.py"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # Add phase10d_test_comparison.png in Phase 10D section
    old_p10d = r"""\section{Phase 10D Independent Held-Out Test Evaluation ($N=27$)}"""
    new_p10d = r"""\section{Phase 10D Independent Held-Out Test Evaluation ($N=27$)}

Figure~\ref{fig:p10d_comparison_chart} visualizes the performance across all four evaluated moderation strategies on the independent held-out test cohort ($N = 27$), comparing four-class accuracy, Macro-F1, prohibited recall, and prohibited false acceptance.

\begin{figure}[H]
    \centering
    \IfFileExists{phase10d_test_comparison.png}{\includegraphics[width=0.95\textwidth]{phase10d_test_comparison.png}}{%
        \IfFileExists{overleaf_figures/phase10d_test_comparison.png}{\includegraphics[width=0.95\textwidth]{overleaf_figures/phase10d_test_comparison.png}}{\fbox{\parbox{0.80\textwidth}{\centering \textbf{Phase 10D Independent Test Evaluation Performance Chart}}}}%
    }
    \caption{Phase 10D Independent Held-Out Test Evaluation ($N = 27$): Empirical Performance Comparison Across Strategy A (RF Alone), Strategy B (Qwen3-VL Alone), Strategy C (Soft Probability Voting), and Strategy D (Hierarchical Safety Fusion).}
    \label{fig:p10d_comparison_chart}
\end{figure}"""
    if old_p10d in c and "fig:p10d_comparison_chart" not in c:
        c = c.replace(old_p10d, new_p10d)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Chapter 6 successfully updated: Phase 10D test comparison chart integrated!")

if __name__ == "__main__":
    update_chapter3()
    update_chapter5()
    update_chapter6()
    
    # Reassemble report
    import sys
    sys.path.insert(0, ".")
    from tools.assemble_report import assemble
    assemble()
    print("Master report successfully reassembled!")
