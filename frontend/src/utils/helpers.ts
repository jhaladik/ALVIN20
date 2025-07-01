// File: frontend/src/utils/helpers.ts
// Replace common lodash functions with native alternatives

// Instead of _.debounce
export const debounce = <T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): ((...args: Parameters<T>) => void) => {
    let timeout: NodeJS.Timeout | null = null
    
    return (...args: Parameters<T>) => {
      if (timeout) clearTimeout(timeout)
      timeout = setTimeout(() => func(...args), wait)
    }
  }
  
  // Instead of _.groupBy
  export const groupBy = <T, K extends string | number>(
    array: T[],
    keyFn: (item: T) => K
  ): Record<K, T[]> => {
    return array.reduce((groups, item) => {
      const key = keyFn(item)
      if (!groups[key]) groups[key] = []
      groups[key].push(item)
      return groups
    }, {} as Record<K, T[]>)
  }
  
  // Instead of _.uniqBy
  export const uniqBy = <T>(array: T[], keyFn: (item: T) => any): T[] => {
    const seen = new Set()
    return array.filter(item => {
      const key = keyFn(item)
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }
  
  // Instead of _.pick
  export const pick = <T extends object, K extends keyof T>(
    obj: T,
    keys: K[]
  ): Pick<T, K> => {
    return keys.reduce((result, key) => {
      if (key in obj) result[key] = obj[key]
      return result
    }, {} as Pick<T, K>)
  }
  
  // Remove lodash dependency:
  // npm uninstall lodash @types/lodash