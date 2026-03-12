using CSV, DataFrames

include("../../src/julia/utils.jl")

df = CSV.read("/Users/arfiligol/Github/Lab/Quantum-Chip-Design-Julia/circuit_model_analysis/Q4_Differential_Pair_Y.csv", DataFrame)

first(df, 5)
names(df)
nrow(df), ncol(df) # 列數、欄數
describe(df)       # 統計摘要（型別、極值、mean 等）

imcol = df[!, "im(Yt(Diff1,Diff1)) []"]
freqs = df[!, "Freq [GHz]"]

idx = argmin(abs.(imcol))   # im(Y) 絕對值最小的列索引
freq_star = freqs[idx]      # 對應的頻率
row_star = df[idx, :]      # 整列資料

Y_m_11 = df[idx, "re(Yt(Comm1,Comm1)) []"] + df[idx, "im(Yt(Comm1,Comm1)) []"] * im
Y_m_12 = df[idx, "re(Yt(Comm1,Diff1)) []"] + df[idx, "im(Yt(Comm1,Diff1)) []"] * im
Y_m_21 = df[idx, "re(Yt(Diff1,Comm1)) []"] + df[idx, "im(Yt(Diff1,Comm1)) []"] * im
Y_m_22 = df[idx, "re(Yt(Diff1,Diff1)) []"] + df[idx, "im(Yt(Diff1,Diff1)) []"] * im

Y_dm_eff = Y_m_22 - (Y_m_12 * Y_m_21) / Y_m_11
display("Real Part Y^{(dm)}_{eff} : $(real.(Y_dm_eff))")

df = CSV.read("/Users/arfiligol/Github/Lab/Quantum-Chip-Design-Julia/circuit_model_analysis/Q4_Two_Pads_Port_Y.csv", DataFrame)

names(df)

imcol = df[!, "im(Yt(Signal9_1_T1,Signal9_1_T1)) []"]
freqs = df[!, "Freq [GHz]"]

idx = argmin(abs.(imcol))   # im(Y) 絕對值最小的列索引
freq_star = freqs[idx]      # 對應的頻率
row_star = df[idx, :]      # 整列資料

Y_two_pads = df[idx, "re(Yt(Signal9_1_T1,Signal9_1_T1)) []"] + df[idx, "im(Yt(Signal9_1_T1,Signal9_1_T1)) []"] * im
display("Real Part Y for Pads Port: $(df[idx, "re(Yt(Signal9_1_T1,Signal9_1_T1)) []"])")
