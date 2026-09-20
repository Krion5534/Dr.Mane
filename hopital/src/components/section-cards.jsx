"use client"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { AlertTriangleIcon, UsersIcon, BabyIcon, HeartPulseIcon } from "lucide-react"

export function SectionCards({ patients = [] }) {
  const total = patients.length
  const critical = patients.filter((p) => p.urgency === 1).length
  const pediatric = patients.filter((p) => p.age < 16).length
  const avgDeathChance = total
    ? (patients.reduce((sum, p) => sum + p.death_chance, 0) / total).toFixed(1)
    : 0

  return (
    <div className="grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-linear-to-t *:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4 dark:*:data-[slot=card]:bg-card">
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Total Patients</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {total.toLocaleString()}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <UsersIcon />
              Live
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">Currently admitted</div>
          <div className="text-muted-foreground">Across all urgency levels</div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Critical Cases</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {critical.toLocaleString()}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <AlertTriangleIcon />
              Urgency 1
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">Needs immediate attention</div>
          <div className="text-muted-foreground">
            {total ? ((critical / total) * 100).toFixed(1) : 0}% of total
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Pediatric Patients</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {pediatric.toLocaleString()}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <BabyIcon />
              Under 16
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">Routed to Pediatrician</div>
          <div className="text-muted-foreground">
            {total ? ((pediatric / total) * 100).toFixed(1) : 0}% of total
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Avg. Death Chance</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {avgDeathChance}%
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <HeartPulseIcon />
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">Across all patients</div>
          <div className="text-muted-foreground">Rises with wait time</div>
        </CardFooter>
      </Card>
    </div>
  )
}