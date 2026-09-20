"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";

import {
  Field,
  FieldContent,
  FieldDescription,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "@/components/ui/field";

import { Input } from "@/components/ui/input";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Checkbox } from "@/components/ui/checkbox";
import { useState } from "react";

export function AddPatient({ open, onOpenChange }) {

  const [isChild, setChild] = useState(true);
  const [highUrgency, setHighUrgency] = useState(false);

  const handleAge = (e) => {
    let age = e.target.value
    console.log(age)
    if (age > 16) setChild(false);
    else setChild(true);
  }

  const handleUrgency = (value) => {
    const highUrgency = [
      "Heart Attack",
      "Cardiac Arrest",
      "Stroke",
      "Brain Hemorrhage",
    ];
    setHighUrgency(highUrgency.includes(value));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[550px]">
        <DialogHeader>
          <DialogTitle>Admit a Patient</DialogTitle>

          <DialogDescription>
            Enter the patient's information below.
          </DialogDescription>
        </DialogHeader>

        <div className="mx-4 max-h-[60vh] overflow-y-auto px-4">
          <form className="space-y-6">

            {/* Patient Name */}
            <Field>
              <FieldLabel htmlFor="patient-name">
                Patient Name
              </FieldLabel>

              <FieldContent>
                <Input
                  id="patient-name"
                  name="name"
                  type="text"
                  placeholder="e.g. Krion"
                />

                <FieldDescription>
                  Patient's name.
                </FieldDescription>
              </FieldContent>
            </Field>


            {/* Age */}
            <Field>
              <FieldLabel htmlFor="patient-age">
                Age
              </FieldLabel>

              <FieldContent>
                <Input
                  id="patient-age"
                  name="age"
                  type="number"
                  min="0"
                  max="120"
                  onChange={(e) => handleAge(e)}
                  placeholder="e.g. 67"
                />
              </FieldContent>
            </Field>


            {/* Arrival */}
            {/* <Field>
              <FieldLabel htmlFor="patient-arrival">
                Arrival Time
              </FieldLabel>

              <FieldContent>
                <Input
                  id="patient-arrival"
                  name="arrival"
                  type="datetime-local"
                  // placeholder="e.g. 120"
                />

                <FieldDescription>
                  Time of arrival in minutes.
                </FieldDescription>
              </FieldContent>
            </Field> */}


            {/* Urgency */}
            <Field>
              <FieldLabel htmlFor="patient-urgency">
                Urgency
              </FieldLabel>

              <FieldContent>
                <Select name="urgency">
                  <SelectTrigger id="patient-urgency">
                    <SelectValue placeholder="Select urgency" />
                  </SelectTrigger>

                  <SelectContent>
                    <SelectItem value="1">
                      1 — Critical
                    </SelectItem>
                    {!highUrgency && (<div>
                      <SelectItem value="2">
                        2 — High
                      </SelectItem>

                      <SelectItem value="3">
                        3 — Moderate
                      </SelectItem>

                      <SelectItem value="4">
                        4 — Low
                      </SelectItem>
                    </div>)}
                  </SelectContent>
                </Select>

                <FieldDescription>
                  1 is the most urgent and 4 is the least urgent.
                </FieldDescription>
              </FieldContent>
            </Field>



            {/* Diagnosis */}
            <Field>
              <FieldLabel htmlFor="patient-diagnosis">
                Diagnosis
              </FieldLabel>

              <FieldContent>
                <Select name="diagnosis" onValueChange={(value) => handleUrgency(value)}>
                  <SelectTrigger id="patient-diagnosis">
                    <SelectValue placeholder="Select diagnosis" />
                  </SelectTrigger>

                  <SelectContent>

                    <SelectItem value="Heart Attack">
                      Heart Attack
                    </SelectItem>

                    <SelectItem value="Cardiac Arrest">
                      Cardiac Arrest
                    </SelectItem>

                    <SelectItem value="Stroke">
                      Stroke
                    </SelectItem>

                    <SelectItem value="Brain Hemorrhage">
                      Brain Hemorrhage
                    </SelectItem>

                    {
                      isChild && <div>
                        <SelectItem value="Pediatric Fever">
                          Pediatric Fever
                        </SelectItem>

                        <SelectItem value="Childhood Asthma">
                          Childhood Asthma
                        </SelectItem>
                      </div>
                    }
                  </SelectContent>
                </Select>

                <FieldDescription>
                  Select patient's diagnosis
                </FieldDescription>
              </FieldContent>
            </Field>

          </form>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>

          <Button type="submit">
            Admit Patient
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}