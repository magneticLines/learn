# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Java learning repository organized **by topic**. Each top-level numbered folder is one study topic and (where applicable) bundles its notes and code together:

- **`notes/`** — Chinese-language study notes (numbered markdown files)
- **`code/`** — Runnable Java examples for that topic

```
00-Java基础/code/        HelloWorld and other entry-level snippets
01-数据结构/             notes/ + code/ (SimpleLinkedList, SimpleHashTable)
02-并发/                 notes/ + code/ (ThreadUnsafeExample)
03-设计模式/             notes/ + code/ (abstractfactory)
04-工程实战/             notes/ + code/ (springbootDemo)
05-git/                  notes/ only
docs/                    Tooling docs (e.g. prompt.md — AI tutor prompt)
```

## Topics

| Folder | Notes topics | Code |
|---|---|---|
| `00-Java基础/` | — | `HelloWorld` |
| `01-数据结构/` | Arrays, linked lists, hash tables, stacks/queues, trees (BST, AVL, red-black) + drawio flowcharts | `SimpleLinkedList`, `SimpleHashTable` |
| `02-并发/` | Locks, synchronized, volatile, final, JUC atomic classes | `ThreadUnsafeExample` |
| `03-设计模式/` | OOP basics, SOLID, design pattern overview, 8 patterns (singleton/factory/abstract-factory/adapter/decorator/proxy/template/strategy/observer/command) | `abstractfactory/` |
| `04-工程实战/` | Spring Security/Shiro, RBAC, login modules, SPI, if-else refactoring | `springbootDemo/` |
| `05-git/` | Windows multi-GitHub account setup | — |

## Teaching code (`*/code/`)

Single-file examples have **no `package` declaration and no `pom.xml`** — run them directly via the IDE (run the `main` method). The `03-设计模式/code/abstractfactory` example is a multi-package program rooted at package `abstractfactory`; mark `03-设计模式/code/` as the source root to run it.

## `04-工程实战/code/springbootDemo`

The one full build project. Spring Boot 2.7.18 web application (Java 11). Entry point: `SheaApplication.java`.

**Build & Run:**
```bash
cd 04-工程实战/code/springbootDemo
mvn clean package          # build JAR
mvn spring-boot:run        # run locally (port 8081)
```

**Test endpoint:** `GET http://localhost:8081/test/hello`

**Deploy to Docker:**
```bash
mvn clean package
./deploy.sh   # builds image, pushes to private registry, deploys via SSH
```
The deploy script targets a private registry at `127.0.0.1:5000` and remote server `172.17.97.140` — update `deploy.sh` variables before use.
