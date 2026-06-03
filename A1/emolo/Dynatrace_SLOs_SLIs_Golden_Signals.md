what are the Dynatrace SLOs, SLIs and golden signals to configure to track issues with application resiliency patterns? what are the resilience configuration parameters to track?
--

When monitoring **application resiliency patterns** in **[Dynatrace](https://www.dynatrace.com?utm_source=chatgpt.com)**, the goal is not only to track whether the application is up, but also whether resilience mechanisms (circuit breakers, retries, timeouts, bulkheads, failover, queues, caches, etc.) are operating correctly.

Many organizations monitor availability and latency but miss the fact that their resilience controls are silently degrading until a major outage occurs.

---

# 1. Golden Signals for Resiliency

Start with the four classic SRE golden signals.

| Golden Signal | Purpose                |
| ------------- | ---------------------- |
| Latency       | How long requests take |
| Traffic       | Request volume         |
| Errors        | Failure rate           |
| Saturation    | Resource exhaustion    |

For resiliency engineering, I recommend adding four more:

| Resilience Signal     | Purpose                                     |
| --------------------- | ------------------------------------------- |
| Retry Rate            | Indicates dependency instability            |
| Timeout Rate          | Indicates downstream slowness               |
| Circuit Breaker State | Indicates failing dependencies              |
| Fallback Success Rate | Measures graceful degradation effectiveness |

---

# 2. Core Application SLOs

## Availability SLO

Target:

```text
99.95%+
```

SLI:

```text
Successful Requests / Total Requests
```

Dynatrace Metrics:

```text
builtin:service.successes.server.rate
builtin:service.errors.server.rate
```

---

## Error Rate SLO

Target:

```text
< 0.1%
```

SLI:

```text
Failed Requests / Total Requests
```

---

## Latency SLO

Target:

```text
P95 < 500ms
```

SLI:

```text
95th percentile response time
```

Dynatrace:

```text
builtin:service.response.time
```

---

## Apdex SLO

Target:

```text
> 0.95
```

Measures end-user satisfaction.

---

# 3. Circuit Breaker Resilience Monitoring

For systems using:

* Resilience4j
* Hystrix
* Service Meshes
* API Gateways

Track:

## SLI: Circuit Breaker Open Rate

```text
Open Events / Total Requests
```

Target:

```text
< 0.5%
```

Monitor:

* Open
* Closed
* Half-open

states.

### Important Parameters

| Parameter           | Track |
| ------------------- | ----- |
| Failure Threshold   | Yes   |
| Slow Call Threshold | Yes   |
| Open Duration       | Yes   |
| Half-Open Successes | Yes   |
| Open Count          | Yes   |

---

# 4. Retry Pattern Monitoring

Retries can hide outages.

Track:

## Retry Rate

```text
Retries / Total Requests
```

Target:

```text
< 2%
```

### Configuration Parameters

| Parameter             | Monitor |
| --------------------- | ------- |
| Max Retries           | Yes     |
| Retry Delay           | Yes     |
| Backoff Strategy      | Yes     |
| Retry Success Rate    | Yes     |
| Retry Exhaustion Rate | Yes     |

Important alert:

```text
Retry Rate Spike
```

Often indicates an impending dependency outage.

---

# 5. Timeout Monitoring

Track:

## Timeout Rate

```text
Timeouts / Total Requests
```

Target:

```text
< 0.1%
```

### Parameters

| Parameter          | Monitor |
| ------------------ | ------- |
| Connection Timeout | Yes     |
| Read Timeout       | Yes     |
| Request Timeout    | Yes     |
| Average Wait Time  | Yes     |

---

# 6. Bulkhead Pattern Monitoring

Bulkheads prevent resource exhaustion.

Track:

## Thread Pool Saturation

```text
Active Threads / Max Threads
```

Target:

```text
< 80%
```

### Parameters

| Parameter          | Monitor |
| ------------------ | ------- |
| Max Threads        | Yes     |
| Active Threads     | Yes     |
| Queue Depth        | Yes     |
| Queue Rejections   | Yes     |
| Thread Utilization | Yes     |

---

# 7. Queue Resilience Monitoring

For:

* Apache Kafka
* RabbitMQ
* Amazon SQS

Track:

## Queue Backlog

```text
Pending Messages
```

Target:

```text
Near zero growth
```

### Parameters

| Parameter               | Monitor |
| ----------------------- | ------- |
| Queue Depth             | Yes     |
| Consumer Lag            | Yes     |
| Processing Rate         | Yes     |
| Dead Letter Queue Count | Yes     |
| Message Age             | Yes     |

---

# 8. Cache Resilience Monitoring

For:

* Redis
* Memcached

Track:

## Cache Hit Ratio

Target:

```text
> 90%
```

### Parameters

| Parameter       | Monitor |
| --------------- | ------- |
| Cache Hit Rate  | Yes     |
| Cache Miss Rate | Yes     |
| Evictions       | Yes     |
| Memory Usage    | Yes     |
| Expiration Rate | Yes     |

---

# 9. Database Resilience Monitoring

Track:

## Connection Pool Saturation

Target:

```text
< 80%
```

### Parameters

| Parameter          | Monitor |
| ------------------ | ------- |
| Active Connections | Yes     |
| Idle Connections   | Yes     |
| Pool Exhaustion    | Yes     |
| Query Timeout Rate | Yes     |
| Query Retry Rate   | Yes     |

---

# 10. Failover Monitoring

For active-passive or active-active systems.

## Failover Success Rate

Target:

```text
100%
```

### Parameters

| Parameter             | Monitor |
| --------------------- | ------- |
| Failover Count        | Yes     |
| Recovery Time         | Yes     |
| Promotion Time        | Yes     |
| Health Check Failures | Yes     |
| Split Brain Events    | Yes     |

---

# 11. Error Budget SLO

One of the most important SRE metrics.

Availability Target:

```text
99.95%
```

Allowed Monthly Downtime:

```text
21.6 minutes
```

Track:

```text
Error Budget Remaining
```

Alert when:

```text
Burn Rate > 2x normal
```

---

# 12. Dynatrace Dashboard for Resilience

Recommended executive dashboard:

### Availability

* Availability %
* Error Budget Remaining

### Performance

* P95 Response Time
* P99 Response Time

### Resilience

* Circuit Breaker Opens
* Retry Rate
* Timeout Rate
* Fallback Usage
* Failover Events

### Dependency Health

* Dependency Error Rate
* Dependency Latency
* Dependency Availability

### Infrastructure

* CPU Saturation
* Memory Saturation
* Thread Pool Saturation
* Queue Depth

---

# 13. Most Important Resilience Configuration Parameters to Track

These are the configuration values most likely to cause incidents when misconfigured:

| Pattern         | Key Parameters                                        |
| --------------- | ----------------------------------------------------- |
| Circuit Breaker | Failure Threshold, Slow Call Threshold, Open Duration |
| Retry           | Max Retries, Backoff Delay, Retry Window              |
| Timeout         | Connection Timeout, Read Timeout, Request Timeout     |
| Bulkhead        | Max Threads, Queue Size                               |
| Cache           | TTL, Memory Limit, Eviction Policy                    |
| Queue           | Max Queue Depth, Consumer Concurrency                 |
| Database Pool   | Max Connections, Idle Timeout                         |
| Failover        | Health Check Interval, Recovery Threshold             |

---

# Enterprise Resilience Scorecard

For a production system, I typically recommend the following SLO set:

| SLO                        | Target             |
| -------------------------- | ------------------ |
| Availability               | 99.95%             |
| Error Rate                 | < 0.1%             |
| P95 Latency                | < 500 ms           |
| Retry Rate                 | < 2%               |
| Timeout Rate               | < 0.1%             |
| Circuit Breaker Open Rate  | < 0.5%             |
| Queue Backlog Growth       | 0 sustained growth |
| Cache Hit Ratio            | > 90%              |
| Connection Pool Saturation | < 80%              |
| Error Budget Burn Rate     | < 1x normal        |

These metrics collectively give visibility into both **service health** and **whether the resiliency mechanisms themselves are preventing failures or masking emerging problems**.

