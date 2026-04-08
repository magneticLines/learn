# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Java learning repository with two parts:
- **`wiki/`** — Chinese-language study notes organized by topic (data structures, concurrency, design patterns, engineering projects, git)
- **`code/`** — Runnable Java code examples

## Code Modules

### `code/springbootDemo`
Spring Boot 2.7.18 web application (Java 11). Entry point: `SheaApplication.java`.

**Build & Run:**
```bash
cd code/springbootDemo
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

### `code/java_basic`
Plain Maven project (Java 17 source, Java 11 target) for basic Java concept examples. No Spring Boot — run classes directly via IDE or `mvn exec:java`.

## Wiki Structure

Notes are in Chinese, organized as numbered files within topic folders:

| Folder | Topics |
|---|---|
| `wiki/并发/` | Locks, synchronized, volatile, final, JUC atomic classes |
| `wiki/数据结构/` | Arrays, linked lists, hash tables, stacks/queues, trees (BST, AVL, red-black) |
| `wiki/设计模式/` | OOP basics, SOLID principles, design pattern overview, command pattern |
| `wiki/工程项目/` | Spring Security/Shiro, RBAC, login modules, SPI, if-else refactoring |
| `wiki/git相关/` | Windows multi-GitHub account setup |
