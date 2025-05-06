import SparkMD5 from 'spark-md5'

const CHUNK_SIZE = 5 * 1024 * 1024 // 5MB分片

export const createFileChunks = (file: File): Blob[] => {
  const chunks: Blob[] = []
  let start = 0
  while (start < file.size) {
    const end = Math.min(start + CHUNK_SIZE, file.size)
    chunks.push(file.slice(start, end))
    start = end
  }
  return chunks
}

export const getFileHash = async (file: File): Promise<string> => {
  return new Promise(resolve => {
    const reader = new FileReader()
    reader.onload = e => {
      const spark = new SparkMD5.ArrayBuffer()
      spark.append(e.target!.result)
      resolve(spark.end())
    }
    reader.readAsArrayBuffer(file)
  })
}