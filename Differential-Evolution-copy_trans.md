![](images/Differential-Evolution-copy/a168f81f80d462b79be0063f369141e576a68fce4d0af6e4752a274338c18592.jpg)

Figure 1. An example of a two-dimensional cost function showing its contour lines and the process for generating $v _ { i , G + 1 }$

圖 1。二維成本函數的範例，顯示其等高線以及生成 $v _ { i , G + 1 }$ 的過程

are then mixed with the parameters of another predetermined vector, the target vector, to yield the so-called trial vector. Parameter mixing is often referred to as “crossover” in the ES-community and will be explained later in more detail. If the trial vector yields a lower cost function value than the target vector, the trial vector replaces the target vector in the following generation. This last operation is called selection. Each population vector has to serve once as the target vector so that NP competitions take place in one generation.

接著將其與另一個預先指定的向量——目標向量（target vector）——的參數混合，以產生所謂的試驗向量（trial vector）。參數混合在 ES 社群中通常稱為「交叉（crossover）」，稍後將進一步詳細說明。若試驗向量所對應的成本函數值低於目標向量，則試驗向量會在下一代中取代目標向量。這最後一個操作稱為選擇（selection）。每個種群向量（population vector）都必須恰好作為一次目標向量，因此在一個世代中會進行 NP 次競爭。

More specifically DE’s basic strategy can be described as follows:

更具體地說，DE 的基本策略可描述如下：

## Mutation 變異

For each target vector $x _ { i , G } , i = 1 , 2 , 3 , . . . , \mathrm { N P }$ , a mutant vector is generated according to

對於每個目標向量 $x _ { i , G } , i = 1 , 2 , 3 , . . . , \mathrm { N P }$，會根據生成一個變異向量。

$$
v _ { i , G + 1 } = x _ { r _ { 1 } , G } + F \cdot ( x _ { r _ { 2 } , G } - x _ { r _ { 3 } , G } )\tag{2}
$$

with random indexes $r _ { 1 } , r _ { 2 } , r _ { 3 } \in \{ 1 , 2 , . . . , \mathrm { N P } \}$ , integer, mutually different and $F > 0$ . The randomly chosen integers $r _ { 1 } , r _ { 2 }$ and $r _ { 3 }$ are also chosen to be different from the running index $i ,$ so that NP must be greater or equal to four to allow for this condition. $F$ is a real and constant factor $\in [ 0 , 2 ]$ which controls the amplification of the differential variation $( x _ { r _ { 2 } , G } - x _ { r _ { 3 } , G } )$ . Figure 1 shows a two-dimensional example that illustrates the different vectors which play a part in the generation of $v _ { i , G + 1 }$

具有隨機索引 $r _ { 1 } , r _ { 2 } , r _ { 3 } \in \{ 1 , 2 , . . . , \mathrm { N P } \}$，為整數且彼此互異，並且 $F > 0$。隨機選取的整數 $r _ { 1 } , r _ { 2 }$ 與 $r _ { 3 }$ 也必須與當前索引 $i$ 不同，因此 NP 必須大於或等於四，才能滿足此條件。$F$ 是一個實數且為常數的因子 $\in [ 0 , 2 ]$，用來控制差分變異 $( x _ { r _ { 2 } , G } - x _ { r _ { 3 } , G } )$ 的放大程度。圖 1 顯示了一個二維範例，用以說明在生成 $v _ { i , G + 1 }$ 時所涉及的不同向量。

## Crossover 交叉

In order to increase the diversity of the perturbed parameter vectors, crossover is introduced. To this end, the trial vector:

為了增加擾動參數向量的多樣性，引入了交叉（crossover）。為此，試驗向量：

$$
u _ { i , G + 1 } = ( u _ { 1 i , G + 1 } , u _ { 2 i , G + 1 } , . . . , u _ { D i , G + 1 } )\tag{3}
$$