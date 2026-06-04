import { z } from "zod";

export const projectSchema = z.object({
  title: z.string().min(1, "Title is required").max(500),
  organization: z.string().default(""),
  role: z.string().default(""),
  domain: z.string().default(""),
  summary: z.string().default(""),
  skills: z.string().default(""),
  tools: z.string().default(""),
});

export type ProjectFormData = z.input<typeof projectSchema>;

export const evidenceSchema = z.object({
  title: z.string().min(1, "Title is required").max(500),
  type: z.enum([
    "user_statement",
    "document",
    "portfolio_link",
    "metric",
    "manager_feedback",
    "public_artifact",
  ]),
  description: z.string().default(""),
  url: z.union([z.string().url("Invalid URL"), z.literal("")]).default(""),
  confidence: z.number().min(0).max(1).default(1),
});

export type EvidenceFormData = z.input<typeof evidenceSchema>;
