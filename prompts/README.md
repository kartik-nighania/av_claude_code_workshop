# Agent Prompts

System prompts for the multi-agent engineering team used in the hands-on lab.
Each file is a copy-paste-ready prompt for one Claude session.

| File                     | Agent        | Reads                                  | Writes                          |
| ------------------------ | ------------ | -------------------------------------- | ------------------------------- |
| `architect-agent.md`     | Architect    | feature request                        | `docs/architecture.md`          |
| `security-agent.md`      | Security     | architecture + code                    | `docs/security_findings.json`   |
| `test-agent.md`          | Test         | architecture + code                    | `tests/` + `docs/test_plan.md`  |
| `reviewer-agent.md`      | Reviewer     | architecture + code                    | `docs/review.md`                |
| `orchestrator-agent.md`  | Orchestrator | all four outputs above                 | `docs/action_plan.md`           |

## How to run the team

1. **Architect** first — its doc is the contract everyone else trusts.
2. **Security + Test + Reviewer** in parallel (separate sessions) against that doc.
3. **Orchestrator** last — merges everything into one prioritized action plan.

The golden rule: **one job per agent, done deeply.** Lane discipline (Security
doesn't refactor, Reviewer doesn't re-do security) is what makes the outputs
trustworthy enough to act on without re-reading everything yourself.

### Two ways to use these in Claude Code

- **Manual / multi-session:** open a fresh session per agent, paste the system
  prompt, attach the inputs. You play the engineering lead.
- **As subagents / plan mode:** put the Orchestrator prompt in the driving
  session and have it spawn the specialist agents, passing each the relevant
  files. The Architect runs first; the rest fan out from its blueprint.
