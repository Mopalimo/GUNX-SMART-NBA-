import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { ScrollView, View, Text, StyleSheet, Pressable, useWindowDimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Activity, BarChart3, Brain, ChartNoAxesCombined, History, Home, Radio, Settings, ShieldCheck, Star, Target, Trophy, Wallet } from 'lucide-react-native';

const C = { bg:'#050b16', panel:'#07152d', blue:'#39a8ff', gold:'#f5c518', green:'#26e66d', muted:'#8da4c5', white:'#f4f7ff' };
const picks = [
  ['Lakers vs Warriors','OVER 228.5','1.88',96], ['Knicks vs Raptors','OVER 214.5','1.85',94],
  ['Blazers vs Wolves','UNDER 226.5','1.95',91], ['Spurs vs Pistons','SPURS WIN','1.62',89],
  ['Clippers vs Jazz','CLIPPERS WIN','1.74',87], ['Celtics vs Heat','UNDER 219.5','1.91',88],
  ['Bulls vs Nets','BULLS +4.5','1.87',90], ['Suns vs Kings','OVER 232.5','1.92',89],
  ['Mavs vs Rockets','MAVS WIN','1.78',92], ['Bucks vs Hawks','OVER 225.5','1.86',87]
] as const;
const nav = [
  ['Home',Home],['Daily 10',Trophy],['AI Analysis',Brain],['Odds Center',Wallet],
  ['Performance',ChartNoAxesCombined],['History',History],['Settings',Settings]
] as const;

function Title({text, icon:Icon}:{text:string;icon:any}) {
  return <View style={s.titleRow}><Icon color={C.gold} size={21}/><Text style={s.title}>{text}</Text></View>;
}
function Panel({children}:{children:React.ReactNode}) { return <View style={s.panel}>{children}</View>; }

export default function App() {
  const [active,setActive] = useState('Home');
  const {width} = useWindowDimensions();
  return <SafeAreaProvider><SafeAreaView style={s.safe} edges={['top','left','right']}><StatusBar style="light"/>
    <ScrollView contentContainerStyle={[s.content,{paddingHorizontal:width<390?9:12}]} showsVerticalScrollIndicator={false}>
      <LinearGradient colors={['#08285a','#061329','#030914']} style={s.hero}>
        <View style={s.logo}><Text style={s.crown}>♛</Text><Text style={{fontSize:31}}>🏀</Text><Text style={s.gunx}>GUNX</Text><Text style={s.smart}>SMART NBA</Text></View>
        <View style={{flex:1,alignItems:'center'}}><Text style={s.heroTitle}>SMART <Text style={{color:C.gold}}>NBA</Text></Text><Text style={s.tag}>ANALYZE • PREDICT • WIN</Text><Text style={s.heroSub}>Smarter Picks. Bigger Wins.</Text></View>
        <View style={{alignItems:'center',gap:10}}><Text style={s.nba}>NBA</Text><Settings color={C.gold} size={25}/></View>
      </LinearGradient>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={s.nav}>
        {nav.slice(0,4).map(([label,Icon]:any)=><Pressable key={label} onPress={()=>setActive(label)} style={[s.navItem,active===label&&s.navOn]}><Icon size={17} color={active===label?'#111827':C.blue}/><Text style={[s.navText,active===label&&{color:'#111827'}]}>{label}</Text></Pressable>)}
      </ScrollView>
      <LinearGradient colors={['#ffe54b','#f2aa00','#ffdf39']} style={s.banner}><Text style={{fontSize:38}}>🏀</Text><View style={{flex:1}}><Text style={s.bannerTitle}>NBA DAILY TOP 10 PICKS</Text><Text style={s.bannerSub}>Analyze smart. Bet smart.</Text></View><ChartNoAxesCombined color="#211800" size={29}/></LinearGradient>
      <Panel><Title text="TOP 10 PICKS" icon={Trophy}/><View style={s.tableHead}><Text style={[s.th,{flex:1.5}]}>MATCH / MARKET</Text><Text style={[s.th,{flex:1}]}>PICK</Text><Text style={s.th}>AI</Text></View>
        {picks.map((p,i)=><View key={p[0]} style={s.pickRow}><Text style={s.rank}>{i+1}</Text><View style={{flex:1.5}}><Text style={s.match}>{p[0]}</Text><Text style={s.odds}>Odds {p[2]}</Text></View><Text style={[s.selection,{flex:1}]}>{p[1]}</Text><View style={s.badge}><Text style={s.badgeText}>{p[3]}%</Text></View></View>)}
        <LinearGradient colors={['#ffeb4a','#f3ad00']} style={s.confidence}><Target color="#171300"/><Text style={s.confText}>GUNX AI CONFIDENCE: 91.2%</Text><ChartNoAxesCombined color="#171300"/></LinearGradient>
      </Panel>
      <Panel><Title text="AI ANALYSIS" icon={Brain}/><View style={s.metrics}><View style={{flex:1}}><Text style={s.muted}>WIN PROBABILITY</Text><Text style={s.prob}>72.8%</Text><View style={s.track}><View style={[s.fill,{width:'72.8%'}]}/></View></View><View style={{flex:1,borderLeftWidth:1,borderColor:'#244267',paddingLeft:12}}><Text style={s.muted}>EXPECTED POINTS</Text><Text style={s.points}>224.5</Text><Text style={s.muted}>Model projection</Text></View></View>
        <View style={s.chart}><Text style={s.muted}>PROJECTED SCORING TREND</Text><View style={s.bars}>{[42,57,49,72,63,86,76,94,80,100,88,96].map((h,i)=><View key={i} style={s.barTrack}><View style={[s.bar,{height:h+'%'}]}/></View>)}</View></View>
        <View style={s.strong}><ShieldCheck color="#07150b" size={19}/><Text style={s.strongText}>STRONG PICK</Text><Text style={{marginLeft:'auto',color:'#12351b',fontSize:10}}>Model signal</Text></View>
        <Text style={s.note}>Demo model values only. Confirm injuries, lineups and market odds before betting.</Text>
      </Panel>
      <Panel><Title text="LIVE NBA SCORES" icon={Radio}/><View style={s.scoreRow}><View style={{flex:1}}><Text style={s.team}>LAL · Lakers</Text></View><Text style={s.score}>102 - 98</Text><View style={{flex:1,alignItems:'flex-end'}}><Text style={s.team}>GSW · Warriors</Text><Text style={s.clock}>Q4 02:15</Text></View></View><View style={s.scoreRow}><Text style={[s.team,{flex:1}]}>NYK · Knicks</Text><Text style={s.score}>88 - 84</Text><View style={{flex:1,alignItems:'flex-end'}}><Text style={s.team}>TOR · Raptors</Text><Text style={s.clock}>Q3 04:32</Text></View></View><Text style={s.note}>Sample scores. Connect a licensed live NBA data provider for real-time updates.</Text></Panel>
      <Panel><Title text="ODDS CENTER" icon={Activity}/>{picks.slice(0,4).map(p=><View key={p[0]} style={s.oddsRow}><View style={{flex:1}}><Text style={s.match}>{p[1]}</Text><Text style={s.odds}>{p[0]}</Text></View><Text style={s.oddsValue}>{p[2]}</Text></View>)}<Text style={s.note}>Illustrative decimal odds only.</Text></Panel>
      <LinearGradient colors={['#ffdf28','#f3a900']} style={s.performance}><Title text="PERFORMANCE" icon={ChartNoAxesCombined}/><View style={s.perfRow}>{[['78.5%','SUCCESS RATE'],['+48.7%','PROFIT MARGIN'],['87 / 111','WIN / TOTAL']].map(([v,l])=><View key={l} style={s.perfItem}><Text style={s.perfValue}>{v}</Text><Text style={s.perfLabel}>{l}</Text></View>)}</View></LinearGradient>
      <Text style={s.footer}>GUNX SMART NBA • ANALYZE • PREDICT • WIN</Text>
    </ScrollView>
    <View style={s.bottom}>{nav.slice(0,5).map(([label,Icon]:any)=><Pressable key={label} onPress={()=>setActive(label)} style={s.bottomItem}><Icon size={20} color={active===label?C.gold:'#cbd5e1'}/><Text style={[s.bottomText,active===label&&{color:C.gold}]}>{label==='Daily 10'?'Picks':label==='AI Analysis'?'AI':label==='Odds Center'?'Odds':label}</Text></Pressable>)}</View>
  </SafeAreaView></SafeAreaProvider>;
}

const s=StyleSheet.create({
 safe:{flex:1,backgroundColor:C.bg},content:{paddingTop:8,paddingBottom:14,gap:11},
 hero:{minHeight:130,borderRadius:15,borderWidth:1,borderColor:'#1268c9',padding:10,flexDirection:'row',alignItems:'center'},
 logo:{width:80,alignItems:'center',borderRightWidth:1,borderColor:'#174b83',paddingRight:6},crown:{color:C.gold,fontSize:25,lineHeight:27},gunx:{color:'#fff',fontSize:20,fontWeight:'900',fontStyle:'italic'},smart:{color:C.gold,fontSize:11,fontWeight:'900'},
 heroTitle:{color:'#fff',fontSize:25,fontWeight:'900'},tag:{color:'#dcecff',fontSize:9,fontWeight:'900',letterSpacing:1,marginTop:5},heroSub:{color:'#fff',fontSize:10,fontWeight:'700',fontStyle:'italic',marginTop:6},nba:{color:'#fff',backgroundColor:'#174b9a',borderRadius:5,padding:8,fontWeight:'900'},
 nav:{gap:6},navItem:{height:42,minWidth:94,paddingHorizontal:10,borderRadius:9,borderWidth:1,borderColor:'#123f77',backgroundColor:'#07152c',flexDirection:'row',alignItems:'center',justifyContent:'center',gap:5},navOn:{backgroundColor:C.gold,borderColor:'#ffe77a'},navText:{color:'#e6f0ff',fontSize:10,fontWeight:'700'},
 banner:{minHeight:76,borderRadius:12,borderWidth:2,borderColor:'#fff17c',flexDirection:'row',alignItems:'center',paddingHorizontal:10,gap:8},bannerTitle:{color:'#171200',fontSize:17,fontWeight:'900',fontStyle:'italic'},bannerSub:{color:'#171200',fontSize:14,fontWeight:'900',fontStyle:'italic',textAlign:'center'},
 panel:{backgroundColor:C.panel,borderColor:'#087cf2',borderWidth:1.2,borderRadius:14,padding:11},titleRow:{flexDirection:'row',alignItems:'center',gap:8,marginBottom:8},title:{color:C.gold,fontSize:17,fontWeight:'900',fontStyle:'italic'},
 tableHead:{flexDirection:'row',borderTopWidth:1,borderBottomWidth:1,borderColor:'#173a68',paddingVertical:7},th:{color:'#e6efff',fontWeight:'800',fontSize:9,width:42},
 pickRow:{flexDirection:'row',alignItems:'center',minHeight:46,borderBottomWidth:1,borderColor:'#10294d',gap:5},rank:{color:'#9cb4d4',fontSize:11,fontWeight:'800',width:17},match:{color:'#f2f6ff',fontWeight:'700',fontSize:10},odds:{color:'#8299b9',fontSize:9,marginTop:3},selection:{color:C.gold,fontSize:9,fontWeight:'900'},badge:{minWidth:40,backgroundColor:'#0b3829',borderRadius:6,paddingVertical:5,alignItems:'center'},badgeText:{color:'#4cff8a',fontSize:10,fontWeight:'900'},
 confidence:{borderRadius:9,padding:9,flexDirection:'row',alignItems:'center',justifyContent:'space-between',marginTop:9},confText:{color:'#171200',fontSize:12,fontWeight:'900'},
 metrics:{flexDirection:'row',gap:12,paddingVertical:5},muted:{color:C.muted,fontSize:9,fontWeight:'800',letterSpacing:.5},prob:{color:'#fff',fontSize:30,fontWeight:'900'},points:{color:C.blue,fontSize:28,fontWeight:'900',marginTop:5},track:{height:8,backgroundColor:'#152c4c',borderRadius:8,overflow:'hidden',marginTop:6},fill:{height:'100%',backgroundColor:C.green},
 chart:{backgroundColor:'#07152b',borderRadius:9,padding:9,borderWidth:1,borderColor:'#153c70',marginTop:6},bars:{height:58,flexDirection:'row',alignItems:'flex-end',gap:4,marginTop:8},barTrack:{flex:1,height:'100%',justifyContent:'flex-end',backgroundColor:'#102846',borderRadius:3,overflow:'hidden'},bar:{width:'100%',backgroundColor:'#258bff',borderRadius:3},
 strong:{flexDirection:'row',alignItems:'center',gap:7,backgroundColor:'#27e45e',borderRadius:8,padding:9,marginTop:9},strongText:{color:'#07150b',fontWeight:'900',fontSize:13},note:{color:'#8294ae',fontSize:9,lineHeight:13,marginTop:7},
 scoreRow:{flexDirection:'row',alignItems:'center',paddingVertical:10,borderTopWidth:1,borderColor:'#142f54'},team:{color:'#fff',fontWeight:'800',fontSize:11},score:{color:'#fff',fontWeight:'900',fontSize:17},clock:{color:C.gold,fontSize:9,fontWeight:'800',marginTop:2},
 oddsRow:{flexDirection:'row',alignItems:'center',paddingVertical:8,borderTopWidth:1,borderColor:'#142f54'},oddsValue:{color:'#fff',backgroundColor:'#155dbb',overflow:'hidden',borderRadius:7,paddingHorizontal:13,paddingVertical:5,fontWeight:'900'},
 performance:{borderRadius:13,padding:11},perfRow:{flexDirection:'row',gap:5},perfItem:{flex:1,alignItems:'center',backgroundColor:'#ffffff40',borderRadius:8,paddingVertical:9},perfValue:{color:'#111827',fontWeight:'900',fontSize:14},perfLabel:{color:'#302400',fontWeight:'800',fontSize:8,marginTop:3},
 footer:{color:C.muted,textAlign:'center',fontSize:9,letterSpacing:1,padding:6},bottom:{flexDirection:'row',backgroundColor:'#030b18',borderTopWidth:1,borderColor:'#1558a4',paddingTop:8,paddingBottom:5},bottomItem:{flex:1,alignItems:'center',gap:4},bottomText:{color:'#d4e0f2',fontSize:8,fontWeight:'700'}
});