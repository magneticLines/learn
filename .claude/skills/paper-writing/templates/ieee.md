# IEEE Conference / Journal Paper Template

> Target: IEEE transactions, conferences (e.g., CVPR, ICML, NeurIPS with IEEE proceedings)

## Structure

```latex
\documentclass[conference]{IEEEtran}

% --- Title & Authors ---
\title{Paper Title}
\author{
  \IEEEauthorblockN{Author One}
  \IEEEauthorblockA{Department, University \\ City, Country \\ email@example.com}
}

\begin{document}
\maketitle

% --- Abstract ---
\begin{abstract}
<!-- 150–250 words, no citations -->
\end{abstract}

\begin{IEEEkeywords}
keyword1, keyword2, keyword3
\end{IEEEkeywords}

% --- Sections ---
\section{Introduction}
\section{Related Work}
\section{Methodology}
\section{Experiments}
\subsection{Setup}
\subsection{Results}
\section{Conclusion}

% --- References ---
\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
```

## Notes
- Two-column format
- Figures: `\begin{figure}[t]` at top of column
- Tables: use `\begin{table}[t]` with `\caption{}` above the table
- Max pages: check specific venue requirements
