export function getCountsAndLabelsForChart(data){
    let labels = []
    let counts = []
    for (const [key, value] of Object.entries(data)){
      labels.push(key)
      counts.push(value.length)
    }
    return [labels, counts]
  }
