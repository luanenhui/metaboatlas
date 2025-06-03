suppressPackageStartupMessages(require(argparse))
suppressPackageStartupMessages(require(RODBC))
options(stringsAsFactors = FALSE)

# --- MS2 similarity algorithm --- #
{
  #' translate Da to ppm
  #' 
  #' Calculating difference of two m/z, then convert diff into ppm
  #' 
  #' @param mz numeric vector, m/z values sorted by inreasing
  #' @param mz.ppm.thr numeric, threshold of ppm difference
  #' @return vector, ppm difference of m/z with the first m/z
  #' @examples 
  #' \donttest{
  #'   GetDiffMZppm(c(100.01,100.02, 100.03))
  #' }
  GetDiffMZppm <- function(mz, mz.ppm.thr = NULL) {
    mz.diff <- diff(mz) / mz[-1] * 1e6
    if (!is.null(mz.ppm.thr)) {
      idx <- which(mz[-1] <= mz.ppm.thr)
      mz.diff[idx] <- mz.diff[idx] * mz[-1][idx] / mz.ppm.thr
    }
    mz.diff
  }
  
  
  #' group m/z based on m/z tolerance
  #'
  #' As MassSpectrometry has fluctuate in m/z detection, one ion can be detected as two similar m/z, thus we need to combine these two m/z.
  #' After Combining, m/z is the mean, and intensity is the sum.
  #' @param spec numeric matrix, columns are "mz" and "intensity", represents an MS2 spectrum
  #' @param ppm.ms2match numeric, m/z tolerance of MS2 in ppm mode
  #' @param mz.ppm.thr used in GetDiffMZppm function
  #' @return MS2 spectrum
  MatchSpec <- function(spec, ppm.ms2match = 30, mz.ppm.thr = 400) {
    while (TRUE) {
      mz.diff.ppm <- GetDiffMZppm(spec[, 'mz'], mz.ppm.thr = mz.ppm.thr)
      idx <- which(mz.diff.ppm < ppm.ms2match)
      if (length(idx) > 0) {
        i <- tail(idx, 1)
        j <- which.max(spec[c(i, i + 1), 'intensity'])
        spec[i, 'intensity'] <- spec[i + j - 1, 'intensity']
        i2 <- i + 1
        spec[i, 'mz'] <- spec[i2, 'mz']
        spec <- spec[-i - 1, , drop = FALSE]
      } else {
        break
      }
    }
    return(spec)
  }
  
  #' combine two MS2 spectrum based on m/z
  #' 
  #' @param spec.exp MS2 spectrum
  #' @param spec.lib MS2 spectrum
  #' @param ppm.ms2match m/z tolerance of MS2 
  #' @return list, contains m/z alignment exp and lib spectrum
  GetSpec2Match <- function(spec.exp, spec.lib, ppm.ms2match = 30) {
    
    # align m/z of spec.exp and spec.lib
    mz.pool   <- sort(c(spec.exp[, 1], spec.lib[, 1]))	# combine mz
    spec.exp.pool = spec.lib.pool = cbind('mz' = mz.pool, 'intensity' = 0)		# construct alignment matrix
    spec.exp.pool[match(spec.exp[,1], spec.exp.pool), "intensity"] = spec.exp[,2]
    spec.lib.pool[match(spec.lib[,1], spec.lib.pool), "intensity"] = spec.lib[,2]
    
    # combine nearby peaks
    pk.spec  <- MatchSpec(spec.exp.pool, ppm.ms2match = ppm.ms2match)	# combine adjacent m/z if GetDiffMZppm < pps.ms2match)
    lib.spec <- MatchSpec(spec.lib.pool, ppm.ms2match = ppm.ms2match)	# combine adjacent m/z if GetDiffMZppm < pps.ms2match)
    
    return(list('exp' = pk.spec, 'lib' = lib.spec))
  }
  
  
  #' compute cosine similarity of two MS2 spectrum
  #'
  #' @param spec.exp experimental MS2 spectrum, columns are "mz" and "intensity"
  #' @param spec.lib reference MS2 spectrum, columns are "mz" and "intensity"
  #' @param sn signal to noise ratio
  #' @param ppm m/z tolerence of MS2
  #' @return cosine similarity of spec.exp and spec.lib
  #' @export
  GetMatchResult = function(spec.exp, spec.lib, sn=3, ppm=30){
    # spec.lib=a; spec.exp=b; sn=10
    colnames(spec.lib)=colnames(spec.exp)=c("mz","intensity")
    mode(spec.lib) = mode(spec.exp) = "numeric"
    spec.lib[,2] = spec.lib[,2]/max(spec.lib[,2])*100
    spec.exp[,2] = spec.exp[,2]/max(spec.exp[,2])*100
    spec.lib.filter = spec.lib[spec.lib[,2]>sn,,drop=FALSE]
    spec.exp.filter = spec.exp[spec.exp[,2]>sn,,drop=FALSE]
    
    # combine spec.lib and spec.exp
    spec2match <- GetSpec2Match(spec.exp, spec.lib,                               # GetSpec2Match returns match(spec.exp, spec.exp+spec.lib) for "exp"
                                ppm.ms2match = ppm)			# and match(spec.lib, spec.exp+spec.lib) + spec.exp for "lib"
    
    # compute cosine similarity
    int.spec = spec2match$exp[,"intensity"]
    int.lib = spec2match$lib[,"intensity"]
    
    score = sum(int.spec*int.lib)/sqrt(sum(int.spec^2) * sum(int.lib^2))
    
    return(score)
  } 
}

parser = ArgumentParser(description = "compare MS2 spectrum in mgf file with datab")
parser$add_argument('-f', dest="file", type="character", required=TRUE,
                    help='mgf format file containing MS2 spectrum')
parser$add_argument('--pimtol', dest='pimtol', type="double",
                    default=0.03,
                    help='Parent Ion Mass Tolerance: (Da)')
parser$add_argument('--mztol', dest='mztol', type="double",
                    default=0.03,
                    help='m/z tolerence of MS2 using Da unit')
parser$add_argument('--cutoff', dest='cutoff', type="double",
                    default=0.5,
                    help='similarity score cutoff')
parser$add_argument('--mode', dest='ionMode', type="integer",
                    required = TRUE,
                    help='ion mode, 1 represents Postive, 2 Negtive, 3 both')
parser$add_argument('--sn', dest='sn', type="integer",
                    default = 3,
                    help='signal to noise ratio')

args <- parser$parse_args()

# args = parser$parse_args(c("-f","F:/uploads/QC-2_HILIC_POS-QC-2.mgf"))

# args = parser$parse_args(c(
#   "-f", "F:/uploads/QC-2 HILIC POS-QC-2.mgf",
#   "--mztol", "0.03",
#   "--pimtol", "0.03",
#   "--mode", "1",
#   "--cutoff", "0.1"
# ))

# set default dict
ionModes = c("Positive"=1, "Negative"=2, "None"=3, "P"=1)

# receive input
file = args$file
mzTol = args$mztol
pimTol = args$pimtol
ionMode = args$ionMode
cutoff = args$cutoff

# preprocessing input
ionMode = names(ionModes)[ionModes==ionMode]
ionMode = sprintf("'%s'",ionMode)
ionMode = paste(ionMode, collapse=",")

# ---- prepare experiment spectra ---- #
{
  raw = suppressWarnings(readLines(file)) 
  start = grep("BEGIN IONS", x=raw)
  end = grep("END IONS", x=raw)
  
  len = min(length(start), 1000)  # maximum spectra to compare
  # len = length(start)
  
  info = lapply(1:len, function(i){
    block = raw[(start[i]+1):(end[i]-1)]
    precursorMZ = block[grep("PEPMASS", block)]
    precursorMZ = as.numeric(unlist(strsplit(precursorMZ, split="="))[2])
    
    precursorRT = block[grep("RTINS", block)]
    precursorRT = as.numeric(unlist(strsplit(precursorRT, split="="))[2])
    
    ms2Rev = grep('=', x=block, perl=TRUE)
    ms2 = block[-ms2Rev]
    if (length(ms2)==0){
      ms2 = matrix(data=1,nrow=1,ncol=2)
    } else {
      ms2 = lapply(ms2, function(x){unlist(strsplit(x,split=" "))})
      ms2 = do.call(rbind, ms2)
      mode(ms2) = "numeric"
    }
    
    colnames(ms2) = c("MZ", "intensity")
    
    list(ms2=ms2, mz=precursorMZ, rt=precursorRT)
  })
}

# ---- connect to database ---- #
{
  conn = odbcConnect("PostgreSQL35W", uid="postgres", pwd="luanenhui1!")
}

# ----- processing each spectra ----- #
MS2 = sapply(1:length(info), function(i){
# MS2 = sapply(2732, function(i){
  # print(i)
  x = info[[i]]
  spec.exp = x$ms2
  # ----- get MS2 from database ----- #
  mz = x$mz
  tolerance = pimTol
  ionMode = ionMode
  sql = sprintf("select * from spectra where abs(\"PrecursorMZ\" - %s) < %s AND \"IonMode\" in (%s)", mz, tolerance, ionMode)
  result = sqlQuery(conn, sql)
  
  if (nrow(result)==0){
    return(NA)
  } else {
    # process MS2 in result
    MS2 = apply(result, 1, function(x){
      mz = as.numeric(unlist(strsplit(x["MZ"], split=",")))
      intensity = as.numeric(unlist(strsplit(x["Intensity"], split=",")))
      if (length(mz)!=length(intensity)){
        result = data.frame(mz=1, intensity=1)
      } else {
        result = data.frame(mz=mz, intensity=intensity)
      }
      
      return(result)
    })
    names(MS2) = result[,"SpectraID"]
    
    # filter MS2 whose intensity all equals 0
    flag = sapply(MS2, function(x){mean(x[,2]==0)})
    MS2 = MS2[flag!=1]
    
    # compute similarity score
    score = sapply(MS2, function(lib){
      lib = as.matrix(lib)
      GetMatchResult(spec.exp = spec.exp, spec.lib = lib, ppm=mzTol*1000)
    })
    
    score.cutoff = score[score>cutoff]
    
    # return result
    if (length(score.cutoff) == 0){
      return(NA)
    } else {
      # query compound info
      rownames(result) = result[,"SpectraID"]
      result = result[names(score.cutoff),]
      compoundIDs = unique(result[,"CompoundID"])
      compoundIDs = sprintf("'%s'",compoundIDs)
      compoundIDs= paste(compoundIDs, collapse=",")
      
      sql = sprintf("select * from Compound where \"MAID\" in (%s)", compoundIDs)
      compoundInfo = sqlQuery(conn, sql)
      
      rownames(compoundInfo) = compoundInfo[,1]
      
      # add annotation
      finalResult = lapply(names(score.cutoff), function(name){
        Query = paste("Q",i,sep="")
        SpectraID = name
        similarity = score.cutoff[SpectraID]
        
        Query_PreMZ = x$mz
        Query_RT = x$rt
        # ID = names(score.cutoff)[1]
        
        Spectra_PreMZ = result[SpectraID,"PrecursorMZ"]
        precursorType = result[SpectraID,"PrecursorType"]
        Instrument = result[SpectraID, "InstrumentType2"]
        CE = result[SpectraID,"CollisionEnergy"]
        
        compoundID = result[SpectraID,"CompoundID"]
        Name = compoundInfo[compoundID, "NAME"]
        Formula = compoundInfo[compoundID, "FORMULA"]
        Pubchem = compoundInfo[compoundID, "PUBCHEM"]
        
        MZ = result[SpectraID,"MZ"]
        Intensity = result[SpectraID,"Intensity"]
        
        return(c(Query, SpectraID, similarity, Query_PreMZ, Query_RT,Spectra_PreMZ,precursorType, Instrument, CE, compoundID, Name, Formula, Pubchem, MZ, Intensity))
      })
      
      L1 = sapply(finalResult, paste, sep="", collapse="&")
      L2 = paste(L1, collapse = ";")
      
      return(L2)
    }
  }
  
})
MS2 = MS2[!is.na(MS2)]
MS2 = paste(MS2, collapse = ";")

# close database connection
odbcClose(conn)

cat(MS2)
