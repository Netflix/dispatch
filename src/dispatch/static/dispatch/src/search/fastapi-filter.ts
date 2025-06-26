/**
 * FastAPI Filter Utilities
 *
 * Modern TypeScript implementation for converting frontend filter options
 * to FastAPI-Filter compatible query parameters.
 */

// Type definitions
export interface DateRange {
  start: string | null
  end: string | null
}

export interface EntityWithId {
  id: number
  name?: string
}

export interface IndividualContact {
  email: string
}

export interface Participant {
  email?: string
  individual?: IndividualContact
}

export interface FilterValue {
  [key: string]: unknown
}

export interface TableOptions {
  filters: Record<string, FilterValue>
  sortBy?: string[]
  descending?: boolean[]
  page?: number
  itemsPerPage?: number
  [key: string]: unknown
}

export interface FastAPIFilterParams {
  [key: string]: string | number | boolean | (string | number)[]
}

export interface SortExpression {
  sortBy: string[]
  descending: boolean[]
}

/**
 * Specialized filter parameter builders for different entity types
 */
class FilterParamBuilder {
  private params: FastAPIFilterParams = {}

  /**
   * Add date range filters (e.g., reported_at__gte, reported_at__lte)
   */
  addDateRange(key: string, dateRange: DateRange): this {
    if (dateRange.start) {
      this.params[`${key}__gte`] = dateRange.start
      if (dateRange.end) {
        this.params[`${key}__lte`] = dateRange.end
      }
    }
    return this
  }

  /**
   * Add participant email filters (assignee, reporter)
   */
  addParticipantEmails(key: string, participants: Participant[]): this {
    const emails = participants
      .map((p) => p.email || p.individual?.email)
      .filter((email): email is string => Boolean(email))

    if (emails.length > 0) {
      const paramKey = key === "assignee" ? "assignee_email__in" : "reporter_email__in"
      this.params[paramKey] = emails
    }
    return this
  }

  /**
   * Add entity ID filters (case_type_id__in, project_id__in, etc.)
   */
  addEntityIds(key: string, entities: EntityWithId[], paramName?: string): this {
    const ids = entities
      .map((entity) => entity.id)
      .filter((id): id is number => typeof id === "number")

    if (ids.length > 0) {
      const param = paramName || `${key}_id__in`
      this.params[param] = ids
    }
    return this
  }

  /**
   * Add simple array filter (status__in, etc.)
   */
  addArrayFilter(key: string, values: unknown[]): this {
    const validValues = values.filter((v) => v != null)
    if (validValues.length > 0) {
      this.params[`${key}__in`] = validValues as (string | number)[]
    }
    return this
  }

  /**
   * Add simple key-value parameter
   */
  addSimpleParam(key: string, value: unknown): this {
    if (value != null) {
      this.params[key] = value as string | number | boolean
    }
    return this
  }

  /**
   * Get the built parameters
   */
  build(): FastAPIFilterParams {
    return { ...this.params }
  }
}

/**
 * Maps filter keys to their specialized handlers
 */
const FILTER_HANDLERS = {
  // Participant filters
  assignee: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addParticipantEmails(key, value as Participant[])
  },
  participant: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addParticipantEmails(key, value as Participant[])
  },

  // Entity ID filters
  case_type: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addEntityIds(key, value as EntityWithId[])
  },
  case_priority: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addEntityIds(key, value as EntityWithId[])
  },
  case_severity: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addEntityIds(key, value as EntityWithId[])
  },
  project: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addEntityIds(key, value as EntityWithId[], "project_id__in")
  },
  tag: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addEntityIds(key, value as EntityWithId[], "tag_id__in")
  },
  tag_type: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addEntityIds(key, value as EntityWithId[], "tag_type_id__in")
  },

  // Simple array filters
  status: (builder: FilterParamBuilder, key: string, value: unknown[]) => {
    builder.addArrayFilter(key, value)
  },
} as const

/**
 * Check if a value is a date range object
 */
function isDateRange(value: unknown): value is DateRange {
  return typeof value === "object" && value !== null && "start" in value
}

/**
 * Convert frontend filter options to FastAPI-Filter parameters
 */
export function createFastAPIFilterParams(
  filters: Record<string, FilterValue>
): FastAPIFilterParams {
  const builder = new FilterParamBuilder()

  Object.entries(filters).forEach(([key, value]) => {
    // Handle date ranges
    if (isDateRange(value)) {
      builder.addDateRange(key, value)
      return
    }

    // Handle arrays
    if (Array.isArray(value) && value.length > 0) {
      const validValues = value.filter((v) => v != null)

      if (validValues.length > 0) {
        const handler = FILTER_HANDLERS[key as keyof typeof FILTER_HANDLERS]
        if (handler) {
          handler(builder, key, validValues)
        } else {
          // Default: treat as array filter
          builder.addArrayFilter(key, validValues)
        }
      }
      return
    }

    // Handle single values
    if (value != null && !isDateRange(value)) {
      builder.addSimpleParam(key, value)
    }
  })

  return builder.build()
}

/**
 * Create sorting expression from sortBy and descending arrays
 */
export function createSortExpression(sortBy?: string[], descending?: boolean[]): SortExpression {
  return {
    sortBy: sortBy || [],
    descending: descending || [],
  }
}

/**
 * Convert complete table options to FastAPI-Filter compatible parameters
 */
export function createFastAPIFilterParameters(options: TableOptions): Record<string, unknown> {
  const { sortBy, descending } = createSortExpression(options.sortBy, options.descending)
  const filterParams = createFastAPIFilterParams(options.filters)

  // Create clean options without the processed fields
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, no-unused-vars
  const { filters, sortBy: _sortBy, descending: _descending, ...cleanOptions } = options

  // Add sorting parameters
  const sortParams: Record<string, string> = {}
  if (sortBy.length > 0) {
    const firstSort = sortBy[0]
    const isDescending = descending[0] || false
    sortParams.order_by = isDescending ? `-${firstSort}` : firstSort
  }

  return {
    ...cleanOptions,
    ...filterParams,
    ...sortParams,
  }
}

/**
 * Type-safe parameter validation
 */
export function validateFilterParams(params: FastAPIFilterParams): string[] {
  const errors: string[] = []

  Object.entries(params).forEach(([key, value]) => {
    if (key.includes("__in") && !Array.isArray(value)) {
      errors.push(`Parameter '${key}' should be an array but got ${typeof value}`)
    }

    if (key.includes("__gte") || key.includes("__lte")) {
      if (typeof value !== "string" && !(value instanceof Date)) {
        errors.push(`Date parameter '${key}' should be a string or Date but got ${typeof value}`)
      }
    }
  })

  return errors
}

/**
 * Debug utility to log filter transformation
 */
export function debugFilterTransformation(
  originalFilters: Record<string, FilterValue>,
  fastApiParams: FastAPIFilterParams
): void {
  if (process.env.NODE_ENV === "development") {
    console.group("🔍 Filter Transformation Debug")
    console.log("Original filters:", originalFilters)
    console.log("FastAPI parameters:", fastApiParams)

    const validationErrors = validateFilterParams(fastApiParams)
    if (validationErrors.length > 0) {
      console.warn("⚠️ Validation warnings:", validationErrors)
    }

    console.groupEnd()
  }
}

export default {
  createFastAPIFilterParameters,
  createFastAPIFilterParams,
  createSortExpression,
  validateFilterParams,
  debugFilterTransformation,
}
