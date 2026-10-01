# Contributing

Thanks for your interest in improving this project. We appreciate people taking the time to report problems, share ideas, investigate unexpected behavior, improve documentation, and help us understand how the project is being used.

We use an **issue-first contribution model**. In most cases, the best way to contribute is to start with a GitHub issue so that we can understand the problem, discuss the desired behavior, and agree on the right direction before anyone spends significant time implementing a solution.

**Please wait for a maintainer invitation before opening a pull request.**

## Why we work this way

Writing code is only one part of maintaining a project. Before making a change, we usually need to understand what problem needs to be solved, whether the change fits the project's goals, how it should behave, what compatibility or maintenance costs it may introduce, and whether there is a simpler solution.

Starting with an issue gives contributors and maintainers a chance to build that shared understanding first. It also helps avoid situations where someone spends substantial time implementing a solution that turns out not to fit the project's direction.

A thoughtful bug report, minimal reproduction, investigation, API suggestion, compatibility report, or description of a real-world use case can be just as valuable as a code change. You do not need to provide an implementation for your contribution to be useful.

## Reporting a bug

Please search the existing issues before opening a new one, as the problem may already have been reported or discussed.

A useful bug report should include whichever of the following are relevant:

- a clear description of what happened;
- what you expected to happen instead;
- steps to reproduce the problem;
- a small reproduction or example;
- the version of this project you are using;
- relevant platform, runtime, or dependency versions;
- logs, stack traces, or error messages; and
- any other information that helps narrow down the problem.

Minimal reproductions are especially helpful. If the clearest way to demonstrate a bug is with a small failing test case, please include that test code directly in the issue or link to a minimal reproduction. There is no need to open a pull request simply to demonstrate that a bug exists.

You do not need to know the cause of the problem before reporting it. A clear description of reproducible behavior is already useful.

## Suggesting an improvement

We welcome ideas for improving the project. When possible, begin by explaining the problem or use case rather than starting with a particular implementation.

It is helpful to describe:

- what you are trying to accomplish;
- why the current behavior is difficult or limiting;
- who might benefit from the change;
- an example of how the improved behavior would be used;
- any workarounds you currently rely on; and
- important compatibility or design constraints you already know about.

You are welcome to suggest a possible solution, but you do not need to design the implementation for us. Maintainers may suggest a different approach after considering the wider codebase, compatibility requirements, maintenance costs, or future direction of the project.

Sometimes we may decide not to make a proposed change. That does not mean the issue was unhelpful. Clear reports and proposals help us understand how the project is being used, even when they do not result in code changes.

## Open issues and implementation

An open issue is an invitation to discuss the problem, investigate it, add useful context, or help us understand possible solutions. It is **not automatically an invitation to begin implementing the change**.

If you are interested in implementing an issue, feel free to say so in the discussion. When outside implementation would be useful, a maintainer will say so explicitly. We may also use labels such as `help wanted`, `implementation welcome`, or `good first issue` to indicate that an issue is suitable for an external contributor.

We aim to review new issues within about two weeks, although maintainer availability varies and this is not a guaranteed response time. If an issue has not received a maintainer response after that period, it is reasonable to assume that it is not a current project priority.

Please feel free to solve the problem locally, continue using a workaround that works for you, or revisit the issue later if you have new information. This expectation is intended to avoid leaving contributors waiting indefinitely and to reduce the need for repeated status requests.

## Pull requests

We generally do not review unsolicited pull requests.

Please start with an issue and wait until a maintainer has agreed that the change should be implemented and invited you to work on it.

A pull request is usually appropriate once:

1. the underlying problem or proposed change has been discussed;
2. we have agreed on the general direction; and
3. a maintainer has explicitly invited an implementation.

This keeps the code-review queue focused on changes that the project has already decided it wants to consider.

If you have been invited to submit a pull request, please:

- keep the change focused on the agreed issue;
- avoid unrelated refactoring, cleanup, formatting changes, or additional features;
- include tests when behavior changes;
- update documentation where appropriate;
- explain non-obvious design choices;
- reference the relevant issue; and
- mention any important differences from what was previously discussed.

If the scope changes significantly while you are working, return to the issue before continuing. A short conversation at that point is usually much easier than reviewing a large implementation that has moved away from the agreed direction.

Pull requests opened without prior agreement may be closed without a full code review. This is not a judgment on the quality of the work. It simply means that the project has not agreed to take on that change or spend maintainer time reviewing its implementation.

## Small fixes and documentation

The issue-first approach generally applies to small fixes as well. Even apparently simple changes can sometimes have consequences that are not obvious without broader project context, and keeping one contribution path makes the process easier to understand and maintain.

For very small documentation problems, such as an obvious typo or broken link, simply reporting the location and the correction is already helpful. A maintainer may choose to fix it directly, and there is no need to prepare a pull request just to make the contribution count.

If a documentation change is more substantial, please open an issue describing what is unclear, incorrect, or missing. That gives us a chance to agree on what the documentation should communicate before anyone rewrites a larger section.

## Before opening an invited pull request

Before submitting a pull request that a maintainer has invited you to work on, please run the project's local validation checks.

If this repository provides a `DEVELOPMENT.md`, development guide, or equivalent setup documentation, follow the commands documented there. At a minimum, you should:

1. run the relevant test suite and make sure it passes;
2. run the project's formatter and verify that no formatting changes remain;
3. run the project's linter or static-analysis checks;
4. build the project and verify that you have not introduced new warnings or errors; and
5. run any additional checks documented for the part of the project you changed.

Where the repository provides exact commands, use those commands rather than equivalent alternatives.

If you cannot run one of the required checks in your environment, mention that clearly in the pull request. Knowing what has and has not been validated makes review much easier.

## Good issue contributions

Some of the most valuable contributions do not contain code. We especially appreciate:

- minimal bug reproductions;
- failing test cases that demonstrate a real problem;
- compatibility reports;
- investigations that narrow down the cause of a problem;
- examples of confusing or undocumented behavior;
- measurements and benchmarks;
- API usability feedback;
- real-world use cases;
- documentation gaps;
- accessibility findings; and
- careful testing of proposed fixes.

If you help us understand a problem more clearly, reduce the amount of investigation required, or provide evidence that helps us make a better decision, you have contributed to the project.

## AI-assisted contributions

AI tools can be useful when investigating problems, preparing reproductions, explaining unfamiliar code, or working on an invited implementation. Using such tools is not a problem by itself, but the person submitting the contribution remains responsible for everything they submit.

Please make sure that you:

- verify that reported behavior is real;
- test reproduction steps yourself;
- check technical claims against the actual project;
- understand any code you submit;
- test proposed changes before asking maintainers to review them; and
- can discuss and support the contribution during review.

Contributions containing fabricated APIs, unverified claims, irrelevant generated material, or code that the contributor cannot explain may be closed without further review. High-volume or speculative submissions may also be closed when they create disproportionate investigation work for maintainers.

If you submit a contribution, you are responsible for understanding it well enough to discuss the design, respond to review feedback, and help debug problems in the implementation.

## Security vulnerabilities

Please **do not report security vulnerabilities in public issues, discussions, or pull requests**.

Use the project's private security-reporting mechanism instead. If GitHub private vulnerability reporting is enabled for the repository, use **Security → Report a vulnerability**.

Keeping security reports private gives maintainers an opportunity to investigate and prepare a fix before details are disclosed publicly.

## Questions and early ideas

If GitHub Discussions is enabled, it is a good place for general questions, early-stage ideas, design exploration, usage questions, and proposals that are not yet concrete enough to become actionable issues.

Once a discussion identifies a specific problem or a well-defined piece of work, it can move into an issue. Keeping exploratory conversations separate from actionable work helps the issue tracker remain useful to both maintainers and contributors.

## Licensing

By submitting a contribution to this project, you agree to license that contribution under the repository's open-source license, unless a separate contributor agreement explicitly applies.

This applies to code, tests, documentation, examples, and other material submitted for inclusion in the project. Please only submit material that you have the right to contribute under those terms.

## Maintainer decisions

Not every valid issue will result in a code change. Maintainers may decide not to pursue a proposal because:

- it falls outside the project's scope;
- the ongoing maintenance cost is too high;
- the use case is very specialized;
- the behavior can already be achieved another way;
- it conflicts with compatibility requirements;
- it does not fit the project's direction; or
- it simply is not a current priority.

These decisions are about the project and its maintenance constraints, not about the value of the person who raised the issue. A well-written issue can still provide useful information even when the answer is ultimately that we will not make the change.

We may also close issues that have become inactive, cannot be reproduced, lack enough information to investigate, or no longer reflect the current version of the project. If useful new information becomes available later, it is usually fine to open a new issue or ask whether an existing one should be revisited.

## Community expectations

Please keep discussions constructive, patient, and focused on the technical problem. Maintainers may not always be able to investigate or respond immediately, and contributors may have different levels of familiarity with the project.

To help keep the project manageable, please avoid:

- repeatedly asking for status updates;
- opening duplicate issues to attract attention;
- opening a pull request after being asked to wait;
- tagging individual maintainers unnecessarily; and
- privately contacting maintainers about ordinary project issues.

Keeping project discussions in the project's public contribution channels also makes the resulting context useful to other users and future contributors.

## A simple rule of thumb

If you find a problem, **show us the problem**.

If you have an idea, **explain the use case**.

If you know how you would solve it, **share your thinking in the issue**.

If outside implementation would be helpful, **we will invite you to open a pull request**.

Thanks again for taking the time to help improve the project.