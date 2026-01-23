---
name: production-code-audit
description: "Systematically audit codebase for production readiness covering architecture, security, performance, testing, and enterprise-level quality standards"
---

# Production Code Audit

## Overview

Conduct systematic codebase audits to ensure production-grade quality meeting enterprise standards. This skill provides a structured approach to evaluate code architecture, security, performance, testing coverage, and deployment readiness.

## When to Use This Skill

- Use when preparing codebase for production deployment
- Use when conducting enterprise-level quality audits
- Use when evaluating technical debt
- Use when performing pre-acquisition due diligence
- Use when transitioning from prototype to production
- Use when establishing quality baselines
- Use when ensuring corporate coding standards compliance

## How It Works

### Step 1: Architecture Review

Examine overall structure:
- Project organization and modularity
- Separation of concerns
- Design pattern usage
- Dependency management
- Circular dependency detection

### Step 2: Code Quality Analysis

Assess code maintainability:
- Function complexity (cyclomatic complexity < 10)
- Code duplication (DRY principle)
- Naming conventions consistency
- SOLID principles adherence
- Error handling patterns

### Step 3: Security Audit

Check for vulnerabilities:
- SQL injection risks
- XSS vulnerabilities
- Authentication/authorization issues
- Hardcoded secrets
- Input validation gaps
- OWASP Top 10 compliance

### Step 4: Performance Check

Identify bottlenecks:
- N+1 query problems
- Missing database indexes
- Inefficient algorithms
- Large bundle sizes
- Missing caching strategies

### Step 5: Testing Assessment

Evaluate test quality:
- Test coverage percentage
- Critical path testing
- Edge case coverage
- Flaky test identification
- CI/CD pipeline status

### Step 6: Production Readiness

Verify deployment preparedness:
- Environment configuration
- Logging and monitoring setup
- Error tracking integration
- Health check endpoints
- Documentation completeness

## Examples

### Example 1: Quick Audit Checklist

```markdown
## Production Readiness Audit

### Architecture (Grade: B+)
- ✅ Clean separation of concerns
- ✅ Proper dependency injection
- ❌ CRITICAL: Circular dependency in OrderService ↔ PaymentService
- ⚠️ HIGH: UserService has 35 methods (god class)

### Security (Grade: C)
- ❌ CRITICAL: SQL injection in UserRepository.findByEmail()
- ❌ CRITICAL: Hardcoded database password in config
- ❌ HIGH: Admin routes missing authentication
- ⚠️ MEDIUM: Weak password hashing (MD5)

### Performance (Grade: B-)
- ❌ HIGH: N+1 query in OrderService.getOrdersWithItems()
- ⚠️ MEDIUM: Missing Redis caching
- ⚠️ MEDIUM: Bundle size 850KB (target: <200KB)

### Testing (Grade: C+)
- ⚠️ Coverage: 42% (target: 80%+)
- ❌ Payment processing: 0% coverage
- ❌ Authentication: 35% coverage

### Recommendations:
1. Fix critical security issues (1 week)
2. Add authentication to admin routes (2 days)
3. Fix N+1 queries (3 days)
4. Increase test coverage (2 weeks)
```

### Example 2: Security Issue Report

```markdown
## Critical Security Issue

**Severity:** CRITICAL
**File:** `src/repositories/UserRepository.ts`
**Line:** 78

**Issue:** SQL Injection Vulnerability

**Vulnerable Code:**
\`\`\`typescript
// ❌ DANGEROUS
async findByEmail(email: string) {
  const query = \`SELECT * FROM users WHERE email = '\${email}'\`;
  return await this.db.query(query);
}
\`\`\`

**Fix:**
\`\`\`typescript
// ✅ SAFE
async findByEmail(email: string) {
  const query = 'SELECT * FROM users WHERE email = $1';
  return await this.db.query(query, [email]);
}
\`\`\`

**Impact:** Database compromise, data breach
**Priority:** Fix immediately before production
```

### Example 3: Performance Optimization

```markdown
## Performance Issue

**File:** `src/services/DashboardService.ts`
**Impact:** 3.2s response time (target: <200ms)

**Problem:**
\`\`\`typescript
// ❌ Sequential queries (3.2s)
async getDashboard(userId: string) {
  const user = await db.user.findUnique({ where: { id: userId } }); // 200ms
  const orders = await db.order.findMany({ where: { userId } }); // 800ms
  const products = await db.product.findMany({ where: { userId } }); // 1200ms
  return { user, orders, products };
}
\`\`\`

**Solution:**
\`\`\`typescript
// ✅ Parallel queries (1.2s - 62% faster)
async getDashboard(userId: string) {
  const [user, orders, products] = await Promise.all([
    db.user.findUnique({ where: { id: userId } }),
    db.order.findMany({ where: { userId } }),
    db.product.findMany({ where: { userId } })
  ]);
  return { user, orders, products };
}
\`\`\`

**Result:** 3.2s → 1.2s (62% improvement)
```

## Best Practices

### ✅ Do This

- **Prioritize Issues** - Critical → High → Medium → Low
- **Provide Solutions** - Show how to fix, not just what's wrong
- **Measure Impact** - Quantify improvements with metrics
- **Grade Components** - Use A-F grades for clarity
- **Set Timelines** - Realistic estimates for fixes
- **Focus on Critical** - Security and data loss issues first
- **Document Findings** - Create clear audit reports
- **Verify Fixes** - Re-audit after changes

### ❌ Don't Do This

- **Don't Overwhelm** - Prioritize, don't dump 500 issues
- **Don't Be Vague** - Show specific code examples
- **Don't Skip Context** - Consider project stage and requirements
- **Don't Ignore Security** - Security issues are always critical
- **Don't Forget Testing** - Untested code isn't production-ready
- **Don't Skip Documentation** - Code without docs isn't maintainable

## Common Pitfalls

### Problem: Too Many Issues
**Symptoms:** Team paralyzed by 200+ issues
**Solution:** Focus on critical/high priority only, create sprints

### Problem: False Positives
**Symptoms:** Flagging non-issues
**Solution:** Understand context, verify manually, ask developers

### Problem: No Follow-Up
**Symptoms:** Audit report ignored
**Solution:** Create GitHub issues, assign owners, track in standups

## Production Audit Checklist

### Security
- [ ] No SQL injection vulnerabilities
- [ ] No hardcoded secrets
- [ ] Authentication on protected routes
- [ ] Authorization checks implemented
- [ ] Input validation on all endpoints
- [ ] Password hashing with bcrypt (10+ rounds)
- [ ] HTTPS enforced
- [ ] Dependencies have no vulnerabilities

### Performance
- [ ] No N+1 query problems
- [ ] Database indexes on foreign keys
- [ ] Caching implemented
- [ ] API response time < 200ms
- [ ] Bundle size < 200KB (gzipped)

### Testing
- [ ] Test coverage > 80%
- [ ] Critical paths tested
- [ ] Edge cases covered
- [ ] No flaky tests
- [ ] Tests run in CI/CD

### Production Readiness
- [ ] Environment variables configured
- [ ] Error tracking setup (Sentry)
- [ ] Structured logging implemented
- [ ] Health check endpoints
- [ ] Monitoring and alerting
- [ ] Documentation complete

## Audit Report Template

```markdown
# Production Audit Report

**Project:** [Name]
**Date:** [Date]
**Overall Grade:** [A-F]

## Executive Summary
[2-3 sentences on overall status]

**Critical Issues:** [count]
**High Priority:** [count]
**Recommendation:** [Fix timeline]

## Findings by Category

### Architecture (Grade: [A-F])
- Issue 1: [Description]
- Issue 2: [Description]

### Security (Grade: [A-F])
- Issue 1: [Description + Fix]
- Issue 2: [Description + Fix]

### Performance (Grade: [A-F])
- Issue 1: [Description + Fix]

### Testing (Grade: [A-F])
- Coverage: [%]
- Issues: [List]

## Priority Actions
1. [Critical issue] - [Timeline]
2. [High priority] - [Timeline]
3. [High priority] - [Timeline]

## Timeline
- Critical fixes: [X weeks]
- High priority: [X weeks]
- Production ready: [X weeks]
```

## Related Skills

- `@code-review-checklist` - Code review guidelines
- `@api-security-best-practices` - API security patterns
- `@web-performance-optimization` - Performance optimization
- `@systematic-debugging` - Debug production issues
- `@senior-architect` - Architecture patterns

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Google Engineering Practices](https://google.github.io/eng-practices/)
- [SonarQube Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

---

**Pro Tip:** Schedule regular audits (quarterly) to maintain code quality. Prevention is cheaper than fixing production bugs!
