# ACM Conference / Journal Paper Template

> Target: ACM conferences (CHI, SIGCHI, PLDI, etc.) and ACM journals (TOCHI, PACMPL, etc.)

## Structure

```latex
\documentclass[sigconf]{acmart}  % or sigplan, acmsmall, acmlarge

\title{Paper Title}
\subtitle{Optional Subtitle}

\author{Author One}
\affiliation{\institution{University Name} \city{City} \country{Country}}
\email{author@example.com}

\begin{abstract}
% 150-200 words
\end{abstract}

\keywords{keyword1, keyword2, keyword3}

\begin{document}
\maketitle

\section{Introduction}
\section{Related Work}
\section{System / Method}
\section{Evaluation / User Study}
\section{Discussion}
\section{Conclusion}

\begin{acks}
Acknowledgments...
\end{acks}

\bibliographystyle{ACM-Reference-Format}
\bibliography{references}

\end{document}
```

## ACM Reference Format Example
> Firstname Lastname, Firstname Lastname, and Firstname Lastname. 2023. Paper Title. In *Proceedings of CHI '23*. ACM, New York, NY, USA, 14 pages. https://doi.org/10.1145/xxxxx

## Notes
- CHI papers: typically 10–14 pages (including references)
- Author-year citations are used in some ACM venues (`\citep`, `\citet`)
- CCS Concepts and user-defined keywords are required
